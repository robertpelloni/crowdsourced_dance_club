import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions, TextInput, Animated } from 'react-native';
import { AppState } from "react-native";
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
  const [requestHistory, setRequestHistory] = useState([]);
  const [voteHistory, setVoteHistory] = useState([]);

  const [vibeRating, setVibeRating] = useState(5);
  const [techRating, setTechRating] = useState(5);
  const [feedbackComment, setFeedbackComment] = useState("");
  const [authToken, setAuthToken] = useState(null);
  const [myUser, setMyUser] = useState(null);
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [regReferral, setRegReferral] = useState('');
  const [appState, setAppState] = useState(AppState.currentState);

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
    if (authToken) {
        fetchMe();
        fetchHistory();
    }
    return () => {
        ws.current?.close();
        if (hapticTimer.current) clearInterval(hapticTimer.current);
    };
  }, [serverUrl, authToken]);
  useEffect(() => {
    const subscription = AppState.addEventListener("change", nextAppState => {
      if (appState.match(/inactive|background/) && nextAppState === "active") {
        console.log("App has come to the foreground! Reconnecting WebSocket...");
        connect();
      }
      setAppState(nextAppState);
    });
    return () => subscription.remove();
  }, [appState]);


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
    try {
        let response;
        if (type === 'login') {
            const formData = new FormData();
            formData.append('username', username);
            formData.append('password', password);
            response = await fetch(`${API_URL}/api/login`, {
                method: 'POST',
                body: formData
            });
        } else {
            response = await fetch(`${API_URL}/api/register`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    username: username,
                    password: password,
                    referral_code: regReferral || null
                })
            });
        }
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
        console.log("WebSocket Notice:", data.message);
      }
    };

    ws.current.onclose = (e) => {
      setConnected(false);
      console.log('WebSocket closed. Reconnecting...', e.reason);
      // Exponential backoff or simple fixed retry
      setTimeout(() => {
        if (authToken) connect();
      }, 3000);
    };
  };

  const fetchCatalog = async () => {
    try {
        const response = await fetch(`${API_URL}/catalog`);
        const data = await response.json();
        setCatalog(data);
    } catch (err) { console.error('Catalog Fetch Failed:', err); }
  };

  const fetchMe = async () => {
    try {
        const response = await fetch(`${API_URL}/api/me`, {
            headers: { 'Authorization': `Bearer ${authToken}` }
        });
        const data = await response.json();
        if (response.ok) {
            setMyUser(data);
            setVibeStats({
                points: data.points,
                badges: data.badges,
                referral_code: data.referral_code,
                vibe_preference: data.vibe_preference
            });
        }
    } catch (err) { console.error('Me Fetch Failed:', err); }
  };

  const fetchHistory = async () => {
    if (!authToken) return;
    try {
        const reqs = await fetch(`${API_URL}/api/me/history/requests`, { headers: { 'Authorization': `Bearer ${authToken}` } });
        setRequestHistory(await reqs.json());
        const votes = await fetch(`${API_URL}/api/me/history/votes`, { headers: { 'Authorization': `Bearer ${authToken}` } });
        setVoteHistory(await votes.json());
    } catch (err) { console.error('History Fetch Failed:', err); }
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
        console.log("WebSocket Notice:", data.message);
    } catch (err) { alert("Highlight generation failed."); }
  };
  const updateVibePreference = async (pref) => {
    try {
        const response = await fetch(`${API_URL}/api/me`, {
            method: "PATCH",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            },
            body: JSON.stringify({ vibe_preference: pref })
        });
        if (response.ok) {
            setVibeStats(prev => ({ ...prev, vibe_preference: pref }));
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
    } catch (err) { console.error("Vibe Update Failed:", err); }
  };
  const submitFeedback = async () => {
    try {
        const response = await fetch(`${API_URL}/api/feedback`, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "Authorization": `Bearer ${authToken}`
            },
            body: JSON.stringify({
                vibe_rating: vibeRating,
                technical_rating: techRating,
                comment: feedbackComment
            })
        });
        if (response.ok) {
            alert("Feedback submitted!");
            setFeedbackComment("");
            setCurrentView("dance");
            Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
        }
    } catch (err) { console.error("Feedback Submission Failed:", err); }
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
  };

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
  const renderRefineView = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.nowPlayingCard}>
            <Text style={styles.headerTitle}>REFINE THE VIBE</Text>
            <Text style={[styles.metaText, {marginTop:5, marginBottom:20}]}>Your feedback directly influences the AI Conductor.</Text>

            <Text style={styles.sectionLabel}>VIBE ACCURACY (1-5)</Text>
            <View id="rating-vibe" style={{flexDirection:"row", gap:10, marginBottom:20}}>
                {[1,2,3,4,5].map(v => (
                    <TouchableOpacity key={v} style={[styles.transitionBtn, vibeRating === v && {borderColor: "#a020f0"}]} onPress={() => setVibeRating(v)}>
                        <Text style={[styles.transitionText, vibeRating === v && {color: "#a020f0"}]}>{v}</Text>
                    </TouchableOpacity>
                ))}
            </View>

            <Text style={styles.sectionLabel}>TECHNICAL SMOOTHNESS (1-5)</Text>
            <View id="rating-tech" style={{flexDirection:"row", gap:10, marginBottom:20}}>
                {[1,2,3,4,5].map(v => (
                    <TouchableOpacity key={v} style={[styles.transitionBtn, techRating === v && {borderColor: "#a020f0"}]} onPress={() => setTechRating(v)}>
                        <Text style={[styles.transitionText, techRating === v && {color: "#a020f0"}]}>{v}</Text>
                    </TouchableOpacity>
                ))}
            </View>

            <Text style={styles.sectionLabel}>COMMENTS</Text>
            <TextInput
                style={[styles.searchInput, {height: 100, textAlignVertical: "top"}]}
                placeholder="Tell us about transitions, track selection, or bugs..."
                placeholderTextColor="#666"
                multiline
                value={feedbackComment}
                onChangeText={setFeedbackComment}
            />

            <TouchableOpacity style={[styles.actionBtn, {marginTop: 20}]} onPress={submitFeedback}>
                <Text style={styles.actionBtnText}>SUBMIT FEEDBACK</Text>
            </TouchableOpacity>
        </View>
    </ScrollView>
  );


  const renderProfileView = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
        <View style={styles.nowPlayingCard}>
            <Text style={styles.sectionLabel}>DANCER STATUS</Text>
            <View style={{flexDirection:'row', justifyContent:'space-between'}}>
                <Text style={styles.trackTitle}>Vibe Points: {vibeStats.points}</Text>
                <Text style={[styles.matchText, {color:'#a020f0'}]}>{vibeStats.vibe_preference}</Text>
            </View>
            <View style={styles.meterBase}>
                <View style={[styles.meterFill, { width: `${(vibeStats.points % 100)}%`, backgroundColor: '#a020f0' }]} />
            </View>
            <Text style={styles.energyStatus}>LEVEL {Math.floor(vibeStats.points / 100) + 1}</Text>

            <View style={{marginTop: 20, padding: 15, backgroundColor: 'rgba(0,255,204,0.05)', borderRadius: 10, borderWidth: 1, borderColor: 'rgba(0,255,204,0.1)'}}>
                <Text style={[styles.sectionLabel, {color: '#00ffcc', marginBottom: 5}]}>YOUR REFERRAL CODE</Text>
                <Text style={[styles.trackTitle, {fontSize: 24, letterSpacing: 2}]}><Text id="profile-referral-code">{vibeStats.referral_code || '--------'}</Text></Text>
                <Text style={[styles.metaText, {fontSize: 10}]}>Share this! You both get 50 bonus points.</Text>
            </View>
        </View>

        <TouchableOpacity style={styles.actionBtn} onPress={generateHighlights}>
            <Text style={styles.actionBtnText}>🎬 GET SET HIGHLIGHTS</Text>
        </TouchableOpacity>

        <Text style={styles.sectionLabel}>SET VIBE PREFERENCE</Text>
        <View style={styles.transitionVoteGrid}>
            {["Psytrance", "Techno", "Progressive", "Ambient"].map(genre => (
                <TouchableOpacity
                    key={genre}
                    style={[styles.transitionBtn, vibeStats.vibe_preference === genre && {borderColor: "#a020f0"}]}
                    onPress={() => updateVibePreference(genre)}
                >
                    <Text style={[styles.transitionText, vibeStats.vibe_preference === genre && {color: "#a020f0"}]}>{genre.toUpperCase()}</Text>
                </TouchableOpacity>
            ))}
        </View>

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

        <Text style={styles.sectionLabel}>RECENT CONTRIBUTIONS</Text>
        <View style={{marginBottom: 20}}>
            {requestHistory.slice(0, 3).map((r, i) => (
                <View key={r.id + i} style={styles.leaderboardItem}>
                    <Text style={styles.navTextActive}>Request: {r.title}</Text>
                    <Text style={[styles.matchText, {color: r.status === 'ACCEPTED' ? '#00ffcc' : '#ff3366'}]}>{r.status}</Text>
                </View>
            ))}
            {voteHistory.slice(0, 3).map((v, i) => (
                <View key={v.id + i} style={styles.leaderboardItem}>
                    <Text style={styles.navTextActive}>Voted: {v.title}</Text>
                    <Text style={styles.matchText}>+1 VOTE</Text>
                </View>
            ))}
        </View>

        <Text style={styles.sectionLabel}>TOP DANCERS (LEADERBOARD)</Text>
        <View style={{marginTop: 10}}>
            {leaderboard.map((u, i) => (
                <View key={(u.user_id || u.username) + i} style={styles.leaderboardItem}>
                    <Text style={styles.navTextActive}>{i+1}. {u.username || u.user_id}</Text>
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
                <TextInput
                    style={[styles.searchInput, {marginTop:10}]}
                    placeholder="Referral Code (Optional)"
                    placeholderTextColor="#666"
                    value={regReferral}
                    onChangeText={setRegReferral}
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
        {currentView === "refine" && renderRefineView()}
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
            <TouchableOpacity onPress={() => setCurrentView("refine")}>
                <Text style={currentView === "refine" ? styles.navTextActive : styles.navText}>REFINE</Text>
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
