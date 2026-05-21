import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions } from 'react-native';
import * as Haptics from 'expo-haptics';

const SERVER_URL = 'ws://localhost:8000/ws/clubgoer';

export default function App() {
  const [currentTrack, setCurrentTrack] = useState(null);
  const [queue, setQueue] = useState([]);
  const [connected, setConnected] = useState(false);
  const [playbackPos, setPlaybackPos] = useState(0);
  const [energyTrend, setEnergyTrend] = useState('stable');
  const [isPeakMode, setIsPeakMode] = useState(false);
  const ws = useRef(null);

  useEffect(() => {
    connect();
    return () => ws.current?.close();
  }, []);

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

        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
    };

    ws.current.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000);
    };
  };

  const castVote = (trackId) => {
    if (ws.current?.readyState === WebSocket.OPEN) {
      ws.current.send(JSON.stringify({
        action: 'VOTE_TRACK',
        track_id: trackId
      }));
      Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      <View style={styles.header}>
        <Text style={styles.headerTitle}>ALGORYTHM</Text>
        <View style={[styles.statusDot, { backgroundColor: connected ? '#00ff00' : '#ff0000' }]} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {renderEnergyMeter()}

        {currentTrack && (
          <View style={styles.nowPlayingCard}>
            <Text style={styles.sectionLabel}>NOW PLAYING</Text>
            <Text style={styles.trackTitle}>{currentTrack.title}</Text>
            <Text style={styles.trackArtist}>{currentTrack.artist}</Text>
            {renderProgressBar()}
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>{currentTrack.bpm} BPM</Text>
              <Text style={styles.metaText}>{currentTrack.key} ({currentTrack.genre})</Text>
            </View>
          </View>
        )}

        <Text style={styles.sectionLabel}>UPCOMING VIBE</Text>
        {queue.map((track, index) => (
          <TouchableOpacity
            key={track.track.id + index}
            style={styles.queueItem}
            onPress={() => castVote(track.track.id)}
          >
            <View style={styles.queueInfo}>
              <Text style={styles.queueTitle}>{track.track.title}</Text>
              <Text style={styles.queueArtist}>{track.track.artist}</Text>
              <Text style={styles.matchText}>{track.track.genre} • {track.track.key}</Text>
            </View>
            <View style={styles.voteContainer}>
              <Text style={styles.voteCount}>{track.votes || 0}</Text>
              <Text style={styles.voteLabel}>VOTES</Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      <View style={styles.bottomNav}>
        <Text style={styles.navTextActive}>DANCE</Text>
        <Text style={styles.navText}>REQUEST</Text>
        <Text style={styles.navText}>PROFILE</Text>
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#0a0a0a',
  },
  header: {
    padding: 20,
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    borderBottomWidth: 1,
    borderBottomColor: '#1a1a1a',
  },
  headerTitle: {
    color: '#fff',
    fontSize: 24,
    fontWeight: '900',
    letterSpacing: 2,
  },
  statusDot: {
    width: 10,
    height: 10,
    borderRadius: 5,
  },
  scrollContent: {
    padding: 20,
  },
  energyMeterContainer: {
    marginBottom: 30,
  },
  meterBase: {
    height: 8,
    backgroundColor: '#1a1a1a',
    borderRadius: 4,
    overflow: 'hidden',
    marginTop: 5,
  },
  meterFill: {
    height: '100%',
    borderRadius: 4,
  },
  energyStatus: {
    fontSize: 10,
    fontWeight: 'bold',
    marginTop: 5,
    letterSpacing: 1,
  },
  sectionLabel: {
    color: '#666',
    fontSize: 12,
    fontWeight: 'bold',
    marginBottom: 10,
    letterSpacing: 1,
  },
  nowPlayingCard: {
    backgroundColor: '#111',
    padding: 20,
    borderRadius: 15,
    marginBottom: 30,
    borderWidth: 1,
    borderBottomColor: '#333',
  },
  trackTitle: {
    color: '#fff',
    fontSize: 22,
    fontWeight: 'bold',
  },
  trackArtist: {
    color: '#aaa',
    fontSize: 16,
    marginBottom: 15,
  },
  progressContainer: {
    height: 4,
    backgroundColor: '#222',
    borderRadius: 2,
    marginVertical: 10,
  },
  progressBar: {
    height: '100%',
    backgroundColor: '#fff',
    borderRadius: 2,
  },
  metaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
  },
  metaText: {
    color: '#666',
    fontSize: 12,
  },
  queueItem: {
    backgroundColor: '#111',
    padding: 15,
    borderRadius: 10,
    marginBottom: 10,
    flexDirection: 'row',
    alignItems: 'center',
  },
  queueInfo: {
    flex: 1,
  },
  queueTitle: {
    color: '#fff',
    fontSize: 16,
    fontWeight: 'bold',
  },
  queueArtist: {
    color: '#888',
    fontSize: 14,
  },
  matchText: {
    color: '#00ff00',
    fontSize: 10,
    fontWeight: 'bold',
    marginTop: 4,
  },
  voteContainer: {
    alignItems: 'center',
    paddingLeft: 15,
  },
  voteCount: {
    color: '#fff',
    fontSize: 18,
    fontWeight: 'bold',
  },
  voteLabel: {
    color: '#444',
    fontSize: 8,
  },
  bottomNav: {
    flexDirection: 'row',
    justifyContent: 'space-around',
    padding: 20,
    borderTopWidth: 1,
    borderTopColor: '#1a1a1a',
    backgroundColor: '#0a0a0a',
  },
  navText: {
    color: '#444',
    fontSize: 12,
    fontWeight: 'bold',
  },
  navTextActive: {
    color: '#fff',
    fontSize: 12,
    fontWeight: 'bold',
  }
});
