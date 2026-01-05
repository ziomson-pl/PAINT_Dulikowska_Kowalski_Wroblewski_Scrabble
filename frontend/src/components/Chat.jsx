import React, { useState, useEffect, useRef } from 'react';
import { gameAPI, profileAPI } from '../services/api';
import chatService from '../services/chat';
import '../styles/Chat.css';

function Chat({ gameId }) {
  const [messages, setMessages] = useState([]);
  const [newMessage, setNewMessage] = useState('');
  const [profile, setProfile] = useState(null);
  const messagesEndRef = useRef(null);

  useEffect(() => {
    loadProfile();
    loadMessages();
  }, [gameId]);

  useEffect(() => {
    if (profile) {
      chatService.connect(gameId, profile.username, profile.id);
      chatService.onMessage((message) => {
        setMessages(prev => [...prev, message]);
      });

      return () => {
        chatService.disconnect();
      };
    }
  }, [profile, gameId]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const loadProfile = async () => {
    try {
      const response = await profileAPI.getProfile();
      setProfile(response.data);
    } catch (err) {
      console.error('Failed to load profile:', err);
    }
  };

  const loadMessages = async () => {
    try {
      const response = await gameAPI.getMessages(gameId);
      setMessages(response.data);
    } catch (err) {
      console.error('Failed to load messages:', err);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  const handleSendMessage = (e) => {
    e.preventDefault();
    if (!newMessage.trim() || !profile) return;

    chatService.sendMessage(newMessage);
    setNewMessage('');
  };

  return (
    <div className="chat-container">
      <h3>Chat</h3>
      <div className="chat-messages">
        {messages.map((msg, index) => (
          <div 
            key={index} 
            className={`chat-message ${msg.user_id === profile?.id ? 'own-message' : ''}`}
          >
            <div className="message-header">
              <span className="message-username">{msg.username}</span>
              <span className="message-time">
                {new Date(msg.created_at).toLocaleTimeString()}
              </span>
            </div>
            <div className="message-text">{msg.message}</div>
          </div>
        ))}
        <div ref={messagesEndRef} />
      </div>
      <form onSubmit={handleSendMessage} className="chat-input-form">
        <input
          type="text"
          value={newMessage}
          onChange={(e) => setNewMessage(e.target.value)}
          placeholder="Type a message..."
          maxLength={500}
          className="chat-input"
        />
        <button type="submit" className="btn-primary chat-send-btn">
          Send
        </button>
      </form>
    </div>
  );
}

export default Chat;
