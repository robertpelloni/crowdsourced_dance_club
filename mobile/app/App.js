import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions, TextInput, Animated } from 'react-native';
import * as Haptics from 'expo-haptics';
import { BarCodeScanner } from 'expo-barcode-scanner';

export default function App() {
  const [currentView, setCurrentView] = useState('dance');
  const [currentTrack, setCurrentTrack] = useState(null);
  const [queue, setQueue] = useState([]);
  const [catalog, setCatalog] = useState([]);
  const [searchQuery, setSearchQuery] = useState('');
  const [connected, setConnected] = useState(false);
  const [playbackPos, setPlaybackPos] = useState(0);
  const [energyTrend, setEnergyTrend] = useState('stable');
  const [isPeakMode, setIsPeakMode] = useState(false);
  const [targetBPM, setTargetBPM] = useState(145.0);
  const [vibeStats, setVibeStats] = useState({ points: 0, badges: [] });
  const [leaderboard, setLeaderboard] = useState([]);
  const [transitionVotes, setTransitionVotes] = useState({ classic: 0, bass_swap: 0, echo_out: 0, hpf_sweep: 0 });

  const [authToken, setAuthToken] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');

  const [serverUrl, setServerUrl] = useState('localhost:8000');
  const [hasPermission, setHasPermission] = useState(null);
  const [scanned, setScanned] = useState(false);

  const ws = useRef(null);
  const hapticTimer = useRef(null);
  const pulseAnim = useRef(new Animated.Value(1)).current;

  const API_URL = `http://${serverUrl}`;
  const WS_URL = `ws://${serverUrl}/ws/clubgoer${authToken ? `?token=${authToken}` : ''}`;

  useEffect(() => {
    (async () => {
      const { status } = await BarCodeScanner.requestPermissionsAsync();
      setHasPermission(status === 'granted');
    })();
    connect();
    fetchCatalog();
    return () => {
        ws.current?.close();
        if (hapticTimer.current) clearInterval(hapticTimer.current);
    };
  }, [serverUrl]);

  useEffect(() => {
    if (hapticTimer.current) clearInterval(hapticTimer.current);
    if (connected && currentTrack) {
        const beatInterval = (60 / targetBPM) * 1000;
        hapticTimer.current = setInterval(() => {
            if (isPeakMode) Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Heavy);
            else Haptics.selectionAsync();

            const intensity = isPeakMode ? 1.5 : (energyTrend === 'rising' ? 1.3 : 1.15);
            Animated.sequence([
                Animated.timing(pulseAnim, { toValue: intensity, duration: 100, useNativeDriver: true }),
                Animated.timing(pulseAnim, { toValue: 1, duration: 100, useNativeDriver: true })
            ]).start();
        }, beatInterval);
    }
  }, [targetBPM, connected, !!currentTrack, isPeakMode, energyTrend]);

  const handleAuth = async (type) => {
    const formData = new FormData();
    formData.append('username', username);
    formData.append('password', password);

    try {
        const response = await fetch(`${API_URL}/api/${type}`, {
            method: 'POST',
            body: formData
        });
        const data = await response.json();
        if (response.ok) {
            if (type === 'login') {
                setAuthToken(data.access_token);
                Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
            } else {
                alert("Registered! Please login.");
            }
        } else {
            alert(data.detail);
        }
    } catch (err) { console.error(err); }
  };

  const connect = () => {
    if (!authToken) return;
    if (ws.current) ws.current.close();
    ws.current = new WebSocket(WS_URL);

    ws.current.onopen = () => {
      setConnected(true);
      console.log('Connected to Conductor:', WS_URL);
    };

    ws.current.onmessage = (e) => {
      const data = JSON.parse(e.data);
      if (data.type === 'QUEUE_SYNC') {
        setCurrentTrack(data.current_track);
        setQueue(data.queue);
        setPlaybackPos(data.playback_position || 0);
        setEnergyTrend(data.energy_trend || 'stable');
        setIsPeakMode(data.is_peak_mode || false);
        setTargetBPM(data.target_bpm || 145.0);
        setLeaderboard(data.leaderboard || []);
        setTransitionVotes(data.transition_votes || { classic: 0, bass_swap: 0, echo_out: 0, hpf_sweep: 0 });
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      } else if (data.type === 'REQUEST_ACCEPTED' || data.type === 'REQUEST_DENIED' || data.type === 'ERROR') {
        if (data.user_stats) setVibeStats(data.user_stats);
        alert(data.message);
      }
    };

    ws.current.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
  };

  const fetchCatalog = async () => {
    try {
        const response = await fetch(`${API_URL}/catalog`);
        const data = await response.json();
        setCatalog(data);
    } catch (err) { console.error('Catalog Fetch Failed:', err); }
  };

  const handleBarCodeScanned = ({ type, data }) => {
    setScanned(true);
    try {
        const syncData = JSON.parse(data);
        if (syncData.conductor_url) {
            const host = syncData.conductor_url.replace('http://', '').replace('https://', '');
            setServerUrl(host);
            setCurrentView('dance');
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
    } catch (e) {
        alert("Invalid QR Code for CDC Venue");
    }
    setTimeout(() => setScanned(false), 2000);
  };

  const generateHighlights = async () => {
    try {
        const response = await fetch(`${API_URL}/api/render-highlights`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(["track_001", "track_002"])
        });
        const data = await response.json();
        alert(data.message);
    } catch (err) { alert("Highlight generation failed."); }
  };

  const castVote = (trackId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'VOTE_TRACK', track_id: trackId }));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
    }
  };

  const voteTransition = (style) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ action: 'VOTE_TRANSITION', style: style }));
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Medium);
    }
  };

  const requestSong = (trackId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
        ws.current.send(JSON.stringify({ action: 'REQUEST_SONG', track_id: trackId }));
        Haptics.notificationAsync(Haptics.NotificationFeedbackType.Warning);
    }
  };

  const renderProgressBar = () => {
    if (!currentTrack) return null;
    const progress = (playbackPos / currentTrack.duration) * 100 || 0;
    return (
      <View style={styles.progressContainer}>
        <View style={[styles.progressBar, { width: `${progress}%` }]} />
      </View>
    );
  };

  const renderEnergyMeter = () => {
    const energyLevel = isPeakMode ? 100 : (energyTrend === 'rising' ? 70 : (energyTrend === 'falling' ? 30 : 50));
    const color = isPeakMode ? '#ff0000' : (energyTrend === 'rising' ? '#ffaa00' : (energyTrend === 'falling' ? '#00ccff' : '#ffffff'));

    return (
      <View style={styles.energyMeterContainer}>
        <Text style={styles.sectionLabel}>ENERGY METER</Text>
        <View style={styles.meterBase}>
          <View style={[styles.meterFill, { width: `${energyLevel}%`, backgroundColor: color }]} />
        </View>
        <Text style={[styles.energyStatus, { color: color }]}>
          {isPeakMode ? '🔥 PEAK MODE ACTIVE' : energyTrend.toUpperCase()}
        </Text>
      </View>
    );
  };

  const renderDanceView = () => {
    const orbColor = pulseAnim.interpolate({
        inputRange: [1, 1.5],
        outputRange: [
            isPeakMode ? '#ff0000' : (energyTrend === 'rising' ? '#ffaa00' : (energyTrend === 'falling' ? '#00ccff' : '#a020f0')),
            '#ffffff'
        ]
    });

    return (
    <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.visualizerContainer}>
            <Animated.View style={[styles.vibeOrb, {
                transform: [{ scale: pulseAnim }],
                backgroundColor: orbColor,
                shadowColor: orbColor,
                opacity: currentTrack ? 1 : 0.2
            }]} />
            <Animated.View style={[styles.vibeOrb, {
                position: 'absolute',
                transform: [{ scale: pulseAnim.interpolate({inputRange:[1, 1.5], outputRange:[1, 2.5]}) }],
                backgroundColor: orbColor,
                opacity: 0.1
            }]} />
        </View>

        {renderEnergyMeter()}
        {currentTrack && (
          <View style={styles.nowPlayingCard}>
            <Text style={styles.sectionLabel}>NOW PLAYING</Text>
            <Text style={styles.trackTitle}>{currentTrack.title}</Text>
            <Text style={styles.trackArtist}>{currentTrack.artist}</Text>
            {renderProgressBar()}
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>{currentTrack.bpm} BPM (LIVE: {targetBPM})</Text>
              <Text style={styles.metaText}>{currentTrack.key} ({currentTrack.genre})</Text>
            </View>
          </View>
        )}
        <Text style={styles.sectionLabel}>UPCOMING VIBE</Text>
        {queue.length === 0 ? <Text style={styles.emptyText}>Queue is empty. Submit a song!</Text> :
         queue.map((item, index) => (
          <TouchableOpacity key={item.track.id + index} style={styles.queueItem} onPress={() => castVote(item.track.id)}>
            <View style={styles.queueInfo}>
              <Text style={styles.queueTitle}>{item.track.title}</Text>
              <Text style={styles.queueArtist}>{item.track.artist}</Text>
              <Text style={styles.matchText}>{item.track.genre} • {item.track.key}</Text>
            </View>
            <View style={styles.voteContainer}>
              <Text style={styles.voteCount}>{item.votes || 0}</Text>
              <Text style={styles.voteLabel}>VOTES</Text>
            </View>
          </TouchableOpacity>
        ))}

        <Text style={styles.sectionLabel}>VOTE NEXT TRANSITION</Text>
        <View style={styles.transitionVoteGrid}>
            {Object.keys(transitionVotes).map(style => (
                <TouchableOpacity key={style} style={styles.transitionBtn} onPress={() => voteTransition(style)}>
                    <Text style={styles.transitionText}>{style.replace('_', ' ').toUpperCase()}</Text>
                    <Text style={styles.transitionCount}>{transitionVotes[style]}</Text>
                </TouchableOpacity>
            ))}
        </View>
    </ScrollView>
  );

  const renderBrowseView = () => {
    const filteredCatalog = catalog.filter(t =>
        t.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.artist.toLowerCase().includes(searchQuery.toLowerCase()) ||
        t.genre.toLowerCase().includes(searchQuery.toLowerCase())
    );

    return (
        <View style={{flex:1}}>
            <View style={styles.searchContainer}>
                <TextInput
                    style={styles.searchInput}
                    placeholder="Search catalog..."
                    placeholderTextColor="#666"
                    value={searchQuery}
                    onChangeText={setSearchQuery}
                />
            </View>
            <ScrollView contentContainerStyle={styles.scrollContent}>
                {filteredCatalog.map((track) => (
                    <TouchableOpacity key={track.id} style={styles.queueItem} onPress={() => requestSong(track.id)}>
                        <View style={styles.queueInfo}>
                            <Text style={styles.queueTitle}>{track.title}</Text>
                            <Text style={styles.queueArtist}>{track.artist}</Text>
                            <Text style={styles.metaText}>{track.genre} • {track.bpm} BPM • {track.key}</Text>
                        </View>
                        <Text style={styles.requestBtnText}>＋</Text>
                    </TouchableOpacity>
                ))}
            </ScrollView>
        </View>
    );
  };

  const renderProfileView = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.nowPlayingCard}>
            <Text style={styles.sectionLabel}>DANCER STATUS</Text>
            <Text style={styles.trackTitle}>Vibe Points: {vibeStats.points}</Text>
            <View style={styles.meterBase}>
                <View style={[styles.meterFill, { width: `${(vibeStats.points % 100)}%`, backgroundColor: '#a020f0' }]} />
            </View>
            <Text style={styles.energyStatus}>LEVEL {Math.floor(vibeStats.points / 100) + 1}</Text>
        </View>

        <TouchableOpacity style={styles.actionBtn} onPress={generateHighlights}>
            <Text style={styles.actionBtnText}>🎬 GET SET HIGHLIGHTS</Text>
        </TouchableOpacity>

        <Text style={styles.sectionLabel}>EARNED BADGES</Text>
        <View style={styles.badgeGrid}>
            {vibeStats.badges.length === 0 ? <Text style={styles.emptyText}>No badges yet. Request tracks to earn them!</Text> :
             vibeStats.badges.map(b => (
                <View key={b} style={styles.badgeItem}>
                    <Text style={styles.badgeIcon}>🏅</Text>
                    <Text style={styles.badgeName}>{b}</Text>
                </View>
            ))}
        </View>

        <Text style={styles.sectionLabel}>TOP DANCERS (LEADERBOARD)</Text>
        <View style={{marginTop: 10}}>
            {leaderboard.map((u, i) => (
                <View key={u.user_id + i} style={styles.leaderboardItem}>
                    <Text style={styles.navTextActive}>{i+1}. {u.user_id}</Text>
                    <Text style={styles.matchText}>{u.points} PTS</Text>
                </View>
            ))}
        </View>
    </ScrollView>
  );

  const renderSyncView = () => (
    <View style={{flex:1, backgroundColor:'#000'}}>
        {hasPermission === null ? <Text style={{color:'#fff', padding:40}}>Requesting camera permission...</Text> :
         hasPermission === false ? <Text style={{color:'#fff', padding:40}}>No access to camera</Text> :
         <BarCodeScanner
            onBarCodeScanned={scanned ? undefined : handleBarCodeScanned}
            style={StyleSheet.absoluteFillObject}
         />
        }
        <TouchableOpacity style={styles.closeSync} onPress={() => setCurrentView('dance')}>
            <Text style={{color:'#fff', fontWeight:'bold'}}>CANCEL</Text>
        </TouchableOpacity>
    </View>
  );

  if (!authToken && currentView !== 'sync') {
    return (
        <SafeAreaView style={[styles.container, {justifyContent:'center', padding:30}]}>
            <View style={styles.nowPlayingCard}>
                <Text style={styles.headerTitle}>JOIN THE CLUB</Text>
                <TextInput
                    style={[styles.searchInput, {marginTop:20}]}
                    placeholder="Username"
                    placeholderTextColor="#666"
                    value={username}
                    onChangeText={setUsername}
                />
                <TextInput
                    style={[styles.searchInput, {marginTop:10}]}
                    placeholder="Password"
                    placeholderTextColor="#666"
                    secureTextEntry
                    value={password}
                    onChangeText={setPassword}
                />
                <TouchableOpacity style={[styles.actionBtn, {marginTop:20}]} onPress={() => handleAuth('login')}>
                    <Text style={styles.actionBtnText}>LOGIN</Text>
                </TouchableOpacity>
                <TouchableOpacity style={[styles.actionBtn, {borderColor:'#666'}]} onPress={() => handleAuth('register')}>
                    <Text style={[styles.actionBtnText, {color:'#666'}]}>REGISTER</Text>
                </TouchableOpacity>
            </View>
        </SafeAreaView>
    );
  }

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      {currentView !== 'sync' && (
        <View style={styles.header}>
            <View>
            <Text style={styles.headerTitle}>ALGORYTHM</Text>
            <Text style={styles.headerSubtitle}>{serverUrl} • {connected ? 'LIVE' : 'OFFLINE'}</Text>
            </View>
            <TouchableOpacity onPress={() => setCurrentView('sync')}>
                <Text style={{fontSize:24}}>📲</Text>
            </TouchableOpacity>
        </View>
      )}

      <View style={{flex:1}}>
        {currentView === 'dance' && renderDanceView()}
        {currentView === 'request' && renderBrowseView()}
        {currentView === 'profile' && renderProfileView()}
        {currentView === 'sync' && renderSyncView()}
      </View>

      {currentView !== 'sync' && (
        <View style={styles.bottomNav}>
            <TouchableOpacity onPress={() => setCurrentView('dance')}>
                <Text style={currentView === 'dance' ? styles.navTextActive : styles.navText}>DANCE</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setCurrentView('request')}>
                <Text style={currentView === 'request' ? styles.navTextActive : styles.navText}>BROWSE</Text>
            </TouchableOpacity>
            <TouchableOpacity onPress={() => setCurrentView('profile')}>
                <Text style={currentView === 'profile' ? styles.navTextActive : styles.navText}>PROFILE</Text>
            </TouchableOpacity>
        </View>
      )}
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#0a0a0a' },
  header: { padding: 20, flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center', borderBottomWidth: 1, borderBottomColor: '#1a1a1a' },
  headerTitle: { color: '#fff', fontSize: 24, fontWeight: '900', letterSpacing: 2 },
  headerSubtitle: { color: '#a020f0', fontSize: 10, fontWeight: 'bold', letterSpacing: 1, marginTop: 2 },
  statusDot: { width: 10, height: 10, borderRadius: 5 },
  scrollContent: { padding: 20 },
  energyMeterContainer: { marginBottom: 30 },
  meterBase: { height: 8, backgroundColor: '#1a1a1a', borderRadius: 4, overflow: 'hidden', marginTop: 5 },
  meterFill: { height: '100%', borderRadius: 4 },
  energyStatus: { fontSize: 10, fontWeight: 'bold', marginTop: 5, letterSpacing: 1 },
  sectionLabel: { color: '#666', fontSize: 12, fontWeight: 'bold', marginBottom: 10, letterSpacing: 1 },
  nowPlayingCard: { backgroundColor: '#111', padding: 20, borderRadius: 15, marginBottom: 30, borderWidth: 1, borderBottomColor: '#333' },
  trackTitle: { color: '#fff', fontSize: 22, fontWeight: 'bold' },
  trackArtist: { color: '#aaa', fontSize: 16, marginBottom: 15 },
  progressContainer: { height: 4, backgroundColor: '#222', borderRadius: 2, marginVertical: 10 },
  progressBar: { height: '100%', backgroundColor: '#fff', borderRadius: 2 },
  metaRow: { flexDirection: 'row', justifyContent: 'space-between' },
  metaText: { color: '#666', fontSize: 12 },
  queueItem: { backgroundColor: '#111', padding: 15, borderRadius: 10, marginBottom: 10, flexDirection: 'row', alignItems: 'center' },
  queueInfo: { flex: 1 },
  queueTitle: { color: '#fff', fontSize: 16, fontWeight: 'bold' },
  queueArtist: { color: '#888', fontSize: 14 },
  matchText: { color: '#00ff00', fontSize: 10, fontWeight: 'bold', marginTop: 4 },
  voteContainer: { alignItems: 'center', paddingLeft: 15 },
  voteCount: { color: '#fff', fontSize: 18, fontWeight: 'bold' },
  voteLabel: { color: '#444', fontSize: 8 },
  bottomNav: { flexDirection: 'row', justifyContent: 'space-around', padding: 20, borderTopWidth: 1, borderTopColor: '#1a1a1a', backgroundColor: '#0a0a0a' },
  navText: { color: '#444', fontSize: 12, fontWeight: 'bold' },
  navTextActive: { color: '#fff', fontSize: 12, fontWeight: 'bold' },
  searchContainer: { padding: 20, borderBottomWidth: 1, borderBottomColor: '#1a1a1a' },
  searchInput: { backgroundColor: '#111', color: '#fff', padding: 15, borderRadius: 10, fontSize: 14 },
  requestBtnText: { color: '#00ffcc', fontSize: 24, fontWeight: 'bold', paddingLeft: 10 },
  emptyText: { color: '#444', fontSize: 12, fontStyle: 'italic', textAlign: 'center', marginTop: 20 },
  badgeGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10 },
  badgeItem: { backgroundColor: '#111', padding: 15, borderRadius: 10, alignItems: 'center', width: (Dimensions.get('window').width - 60) / 2 },
  badgeIcon: { fontSize: 32, marginBottom: 5 },
  badgeName: { color: '#fff', fontSize: 10, fontWeight: 'bold', textAlign: 'center' },
  leaderboardItem: { flexDirection: 'row', justifyContent: 'space-between', padding: 10, borderBottomWidth: 1, borderBottomColor: '#111' },
  actionBtn: { backgroundColor: 'rgba(0,255,204,0.1)', padding: 15, borderRadius: 10, marginBottom: 20, borderWidth: 1, borderColor: '#00ffcc' },
  actionBtnText: { color: '#00ffcc', fontWeight: 'bold', textAlign: 'center' },
  closeSync: { position: 'absolute', bottom: 40, alignSelf: 'center', backgroundColor: 'rgba(255,255,255,0.1)', padding: 20, borderRadius: 10 },
  visualizerContainer: { height: 100, justifyContent: 'center', alignItems: 'center', marginBottom: 20 },
  vibeOrb: { width: 50, height: 50, borderRadius: 25, shadowColor: '#fff', shadowRadius: 20, shadowOpacity: 0.5, elevation: 10 },
  transitionVoteGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 10, marginTop: 10 },
  transitionBtn: { backgroundColor: '#1a1a1a', padding: 15, borderRadius: 10, flex: 1, minWidth: '45%', alignItems: 'center', borderWidth: 1, borderColor: '#333' },
  transitionText: { color: '#888', fontSize: 10, fontWeight: 'bold' },
  transitionCount: { color: '#a020f0', fontSize: 18, fontWeight: 'bold', marginTop: 5 }
});
