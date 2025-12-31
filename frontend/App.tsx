import React, { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  Pressable,
  SafeAreaView,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import * as DocumentPicker from 'expo-document-picker';

type Citation = {
  chunk_id: string;
  quote: string;
};

type ChatMessage = {
  role: 'user' | 'assistant';
  content: string;
  citations?: Citation[];
};

const API_BASE_URL =
  process.env.EXPO_PUBLIC_API_BASE_URL ?? 'http://localhost:8000';

export default function App() {
  const [documentId, setDocumentId] = useState('');
  const [ingestionId, setIngestionId] = useState('');
  const [ingestionStatus, setIngestionStatus] = useState('idle');
  const [progress, setProgress] = useState(0);
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [input, setInput] = useState('');
  const [isUploading, setIsUploading] = useState(false);
  const [isChatting, setIsChatting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const pickAndUpload = useCallback(async () => {
    setError(null);
    const result = await DocumentPicker.getDocumentAsync({
      type: 'application/pdf',
      copyToCacheDirectory: true,
    });
    if (result.canceled) {
      return;
    }

    const asset = result.assets[0];
    setIsUploading(true);
    try {
      const formData = new FormData();
      const file = asset.file ?? {
        uri: asset.uri,
        name: asset.name ?? 'document.pdf',
        type: asset.mimeType ?? 'application/pdf',
      };
      formData.append('file', file as unknown as Blob);

      const uploadResponse = await fetch(`${API_BASE_URL}/v1/documents`, {
        method: 'POST',
        body: formData,
      });
      if (!uploadResponse.ok) {
        const text = await uploadResponse.text();
        throw new Error(text || 'Upload failed.');
      }
      const document = await uploadResponse.json();

      setDocumentId(document.id);
      setMessages([]);
      setInput('');

      const ingestionResponse = await fetch(
        `${API_BASE_URL}/v1/documents/${document.id}/ingestions`,
        { method: 'POST' }
      );
      if (!ingestionResponse.ok) {
        const text = await ingestionResponse.text();
        throw new Error(text || 'Failed to start ingestion.');
      }
      const ingestion = await ingestionResponse.json();
      setIngestionId(ingestion.id);
      setIngestionStatus(ingestion.status);
      setProgress(ingestion.progress ?? 0);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error.');
    } finally {
      setIsUploading(false);
    }
  }, []);

  useEffect(() => {
    if (!ingestionId) {
      return undefined;
    }
    if (ingestionStatus === 'ready' || ingestionStatus === 'failed') {
      return undefined;
    }

    const interval = setInterval(async () => {
      try {
        const response = await fetch(
          `${API_BASE_URL}/v1/ingestions/${ingestionId}`
        );
        if (!response.ok) {
          return;
        }
        const ingestion = await response.json();
        setIngestionStatus(ingestion.status);
        setProgress(ingestion.progress ?? 0);
      } catch {
        // Ignore transient polling errors.
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [ingestionId, ingestionStatus]);

  const sendMessage = useCallback(async () => {
    const trimmed = input.trim();
    if (!trimmed || !documentId) {
      return;
    }

    setError(null);
    setIsChatting(true);
    const nextMessages: ChatMessage[] = [
      ...messages,
      { role: 'user', content: trimmed },
    ];
    setMessages(nextMessages);
    setInput('');

    try {
      const response = await fetch(
        `${API_BASE_URL}/v1/documents/${documentId}/chat`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            messages: nextMessages.map((message) => ({
              role: message.role,
              content: message.content,
            })),
            top_k: 3,
            include_citations: true,
          }),
        }
      );
      if (!response.ok) {
        const text = await response.text();
        throw new Error(text || 'Chat request failed.');
      }
      const data = await response.json();
      setMessages([
        ...nextMessages,
        {
          role: 'assistant',
          content: data.answer,
          citations: data.citations,
        },
      ]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Unexpected error.');
      setMessages(nextMessages);
    } finally {
      setIsChatting(false);
    }
  }, [documentId, input, messages]);

  const readyToChat = ingestionStatus === 'ready';
  const progressLabel = Math.round(progress * 100);

  return (
    <SafeAreaView style={styles.safeArea}>
      <View style={styles.container}>
        <View style={styles.header}>
          <Text style={styles.title}>INKB Reading Copilot</Text>
          <Text style={styles.subtitle}>Upload a PDF and chat with it.</Text>
          <Text style={styles.meta}>API: {API_BASE_URL}</Text>
        </View>

        <View style={styles.section}>
          <Pressable
            style={[styles.button, isUploading && styles.buttonDisabled]}
            onPress={pickAndUpload}
            disabled={isUploading}
          >
            <Text style={styles.buttonText}>
              {isUploading ? 'Uploading...' : 'Upload PDF'}
            </Text>
          </Pressable>

          <View style={styles.statusRow}>
            <Text style={styles.statusLabel}>Ingestion status:</Text>
            <Text style={styles.statusValue}>{ingestionStatus}</Text>
            {ingestionStatus !== 'idle' && (
              <Text style={styles.statusValue}>{progressLabel}%</Text>
            )}
          </View>
        </View>

        <View style={styles.section}>
          <Text style={styles.sectionTitle}>Chat</Text>
          <ScrollView style={styles.chat} contentContainerStyle={styles.chatBody}>
            {messages.length === 0 && (
              <Text style={styles.emptyState}>
                Upload a document to start chatting.
              </Text>
            )}
            {messages.map((message, index) => (
              <View
                key={`${message.role}-${index}`}
                style={
                  message.role === 'user'
                    ? styles.messageUser
                    : styles.messageAssistant
                }
              >
                <Text style={styles.messageRole}>
                  {message.role === 'user' ? 'You' : 'Copilot'}
                </Text>
                <Text style={styles.messageText}>{message.content}</Text>
                {message.citations && message.citations.length > 0 && (
                  <View style={styles.citations}>
                    <Text style={styles.citationsTitle}>Citations</Text>
                    {message.citations.map((citation) => (
                      <Text key={citation.chunk_id} style={styles.citationText}>
                        - {citation.quote}
                      </Text>
                    ))}
                  </View>
                )}
              </View>
            ))}
          </ScrollView>

          <View style={styles.chatInputRow}>
            <TextInput
              style={styles.input}
              placeholder={
                readyToChat
                  ? 'Ask something about the document...'
                  : 'Ingestion must finish before chatting.'
              }
              value={input}
              onChangeText={setInput}
              editable={readyToChat && !isChatting}
            />
            <Pressable
              style={[
                styles.button,
                (!readyToChat || isChatting) && styles.buttonDisabled,
              ]}
              onPress={sendMessage}
              disabled={!readyToChat || isChatting}
            >
              <Text style={styles.buttonText}>
                {isChatting ? 'Sending...' : 'Send'}
              </Text>
            </Pressable>
          </View>
          {isChatting && <ActivityIndicator style={styles.spinner} />}
        </View>

        {error && <Text style={styles.error}>{error}</Text>}
      </View>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safeArea: {
    flex: 1,
    backgroundColor: '#f7f7f5',
  },
  container: {
    flex: 1,
    padding: 20,
    gap: 20,
  },
  header: {
    gap: 6,
  },
  title: {
    fontSize: 28,
    fontWeight: '700',
    color: '#1b1b1b',
  },
  subtitle: {
    fontSize: 16,
    color: '#444',
  },
  meta: {
    fontSize: 12,
    color: '#6b6b6b',
  },
  section: {
    backgroundColor: '#ffffff',
    borderRadius: 12,
    padding: 16,
    gap: 12,
    shadowColor: '#000',
    shadowOpacity: 0.05,
    shadowRadius: 12,
    shadowOffset: { width: 0, height: 4 },
  },
  sectionTitle: {
    fontSize: 18,
    fontWeight: '600',
  },
  button: {
    backgroundColor: '#1f6feb',
    paddingVertical: 12,
    paddingHorizontal: 16,
    borderRadius: 8,
    alignItems: 'center',
  },
  buttonDisabled: {
    backgroundColor: '#9bbcf2',
  },
  buttonText: {
    color: '#fff',
    fontWeight: '600',
  },
  statusRow: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 8,
    alignItems: 'center',
  },
  statusLabel: {
    fontSize: 14,
    color: '#555',
  },
  statusValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#1b1b1b',
  },
  chat: {
    maxHeight: 320,
  },
  chatBody: {
    gap: 12,
  },
  emptyState: {
    color: '#777',
    fontStyle: 'italic',
  },
  messageUser: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#e7f0ff',
    gap: 6,
  },
  messageAssistant: {
    padding: 12,
    borderRadius: 10,
    backgroundColor: '#f1f1f1',
    gap: 6,
  },
  messageRole: {
    fontSize: 12,
    fontWeight: '600',
    color: '#555',
  },
  messageText: {
    fontSize: 14,
    color: '#1b1b1b',
  },
  citations: {
    gap: 4,
  },
  citationsTitle: {
    fontSize: 12,
    fontWeight: '600',
    color: '#444',
  },
  citationText: {
    fontSize: 12,
    color: '#555',
  },
  chatInputRow: {
    flexDirection: 'row',
    gap: 8,
    alignItems: 'center',
  },
  input: {
    flex: 1,
    borderWidth: 1,
    borderColor: '#ddd',
    borderRadius: 8,
    paddingHorizontal: 12,
    paddingVertical: 10,
    backgroundColor: '#fff',
  },
  spinner: {
    alignSelf: 'flex-start',
  },
  error: {
    color: '#b42318',
    fontSize: 13,
  },
});
