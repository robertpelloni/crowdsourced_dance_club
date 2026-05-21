import React, { useState, useEffect, useRef } from 'react';
import { StyleSheet, Text, View, ScrollView, TouchableOpacity, SafeAreaView, StatusBar, Dimensions } from 'react-native';
import * as Haptics from 'expo-haptics';

const SERVER_URL = 'ws://localhost:8000/ws/clubgoer'; // Update to venue IP in production

export default function App() {
  const [currentTrack, setCurrentTrack] = useState(null);
  const [queue, setQueue] = useState([]);
  const [connected, setConnected] = useState(false);
  const [playbackPos, setPlaybackPos] = useState(0);
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

        // Haptic pulse on major queue updates
        Haptics.impactAsync(Haptics.ImpactFeedbackStyle.Light);
      }
    };

    ws.current.onclose = () => {
      setConnected(false);
      setTimeout(connect, 3000); // Auto-reconnect
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

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar barStyle="light-content" />

      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.headerTitle}>ALGORYTHM</Text>
        <View style={[styles.statusDot, { backgroundColor: connected ? '#00ff00' : '#ff0000' }]} />
      </View>

      <ScrollView contentContainerStyle={styles.scrollContent}>
        {/* Now Playing */}
        {currentTrack && (
          <View style={styles.nowPlayingCard}>
            <Text style={styles.sectionLabel}>NOW PLAYING</Text>
            <Text style={styles.trackTitle}>{currentTrack.title}</Text>
            <Text style={styles.trackArtist}>{currentTrack.artist}</Text>
            {renderProgressBar()}
            <View style={styles.metaRow}>
              <Text style={styles.metaText}>{currentTrack.bpm} BPM</Text>
              <Text style={styles.metaText}>{currentTrack.key}</Text>
            </View>
          </View>
        )}

        {/* Upcoming Queue */}
        <Text style={styles.sectionLabel}>UPCOMING VIBE</Text>
        {queue.map((track, index) => (
          <TouchableOpacity
            key={track.track_id + index}
            style={styles.queueItem}
            onPress={() => castVote(track.track_id)}
          >
            <View style={styles.queueInfo}>
              <Text style={styles.queueTitle}>{track.title}</Text>
              <Text style={styles.queueArtist}>{track.artist}</Text>
              <Text style={styles.matchText}>{Math.round(track.fit_score * 100)}% MATCH</Text>
            </View>
            <View style={styles.voteContainer}>
              <Text style={styles.voteCount}>{track.votes || 0}</Text>
              <Text style={styles.voteLabel}>VOTES</Text>
            </View>
          </TouchableOpacity>
        ))}
      </ScrollView>

      {/* Bottom Nav Placeholder */}
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
