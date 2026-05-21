import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions, TextInput } from 'react-native';
import * as Haptics from 'expo-haptics';

const SERVER_URL = 'ws://localhost:8000/ws/clubgoer';
const API_URL = 'http://localhost:8000';

export default function App() {
  const [currentView, setCurrentView] = useState('dance'); // 'dance', 'request', 'profile'
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

  const ws = useRef(null);
  const hapticTimer = useRef(null);

  useEffect(() => {
    connect();
    fetchCatalog();
    return () => {
        ws.current?.close();
        if (hapticTimer.current) clearInterval(hapticTimer.current);
    };
  }, []);

  useEffect(() => {
    if (hapticTimer.current) clearInterval(hapticTimer.current);
    if (connected && currentTrack) {
        const beatInterval = (60 / targetBPM) * 1000;
        hapticTimer.current = setInterval(() => {
            Haptics.selectionAsync();
        }, beatInterval);
    }
  }, [targetBPM, connected, !!currentTrack]);

  const connect = () => {
    ws.current = new WebSocket(SERVER_URL);

    ws.current.onopen = () => {
      setConnected(true);
      console.log('Connected to Conductor Server');
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
    } catch (err) { console.error(err); }
  };

  const castVote = (trackId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({ action: 'VOTE_TRACK', track_id: trackId }));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
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

  const renderDanceView = () => (
    <ScrollView contentContainerStyle={styles.scrollContent}>
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
    </ScrollView>
  );

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>ALGORYTHM</Text>
          <Text style={styles.headerSubtitle}>Points: {vibeStats.points}</Text>
        </View>
        <View style={[styles.statusDot, { backgroundColor: connected ? '#00ff00' : '#ff0000' }]} />
      </View>

      <View style={{flex:1}}>
        {currentView === 'dance' && renderDanceView()}
        {currentView === 'request' && renderBrowseView()}
        {currentView === 'profile' && renderProfileView()}
      </View>

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
  badgeName: { color: '#fff', fontSize: 10, fontWeight: 'bold', textAlign: 'center' }
});
