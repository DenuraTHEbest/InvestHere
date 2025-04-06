"use client";

import { useState, useRef, useEffect } from 'react';
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeftIcon, SendIcon, BotIcon, UserIcon, Sparkles } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from 'next/link';
import axios from 'axios';
import { cn } from "@/lib/utils";
import { motion, AnimatePresence } from 'framer-motion'; // For animations

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
  id: string;
};

const TYPING_SPEED = 25; // Typing speed in milliseconds per character

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([]); // Initialize with empty array
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const [senderId] = useState(`user_${Math.random().toString(36).substr(2, 9)}`);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLInputElement>(null);

  // Load messages from localStorage on client-side mount
  useEffect(() => {
    const savedMessages = localStorage.getItem('chatMessages');
    if (savedMessages) {
      setMessages(
        JSON.parse(savedMessages, (key, value) => {
          if (key === 'timestamp') return new Date(value);
          return value;
        })
      );
    } else {
      // Set default welcome message if no messages are saved
      setMessages([
        {
          role: 'assistant',
          content: `👋 Welcome to InvestHere! I'm your AI investment assistant. How can I help you today?`,
          timestamp: new Date(),
          id: `msg-${Date.now()}`,
        },
      ]);
    }
  }, []);

  // Persist messages to localStorage
  useEffect(() => {
    localStorage.setItem('chatMessages', JSON.stringify(messages));
  }, [messages]);

  // Scroll to bottom when messages change
  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTo({
        top: scrollAreaRef.current.scrollHeight,
        behavior: 'smooth',
      });
    }
  }, [messages]);

  // Focus input on mount
  useEffect(() => {
    inputRef.current?.focus();
  }, []);

  const handleSend = async () => {
    if (!input.trim()) return;

    // Add user message to chat
    const userMessage: Message = {
      role: 'user',
      content: input,
      timestamp: new Date(),
      id: `msg-${Date.now()}`,
    };
    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setIsTyping(true);

    try {
      // Send message to Rasa
      const response = await axios.post('/api/rasa/webhooks/rest/webhook', {
        sender: senderId,
        message: input,
      });
      console.log('Rasa response:', response.data);

      const rasaResponse = response.data;
      if (rasaResponse && rasaResponse.length > 0) {
        // Simulate typing animation for bot response
        for (const msg of rasaResponse) {
          const botMessage: Message = {
            role: 'assistant',
            content: '',
            timestamp: new Date(),
            id: `msg-${Date.now()}`,
          };
          setMessages((prev) => [...prev, botMessage]);

          // Simulate typing effect
          for (let i = 0; i < msg.text.length; i++) {
            await new Promise((resolve) => setTimeout(resolve, TYPING_SPEED));
            setMessages((prev) => {
              const updatedMessages = [...prev];
              const lastMessage = updatedMessages[updatedMessages.length - 1];
              lastMessage.content = msg.text.slice(0, i + 1);
              return updatedMessages;
            });
          }
        }
      } else {
        setMessages((prev) => [
          ...prev,
          {
            role: 'assistant',
            content: 'No response from bot.',
            timestamp: new Date(),
            id: `msg-${Date.now()}`,
          },
        ]);
      }
    } catch (error) {
      console.error('Error communicating with Rasa:', error);
      setMessages((prev) => [
        ...prev,
        {
          role: 'assistant',
          content: 'Error: Could not reach the bot.',
          timestamp: new Date(),
          id: `msg-${Date.now()}`,
        },
      ]);
    } finally {
      setIsTyping(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col">
      {/* Chat Header */}
      <header className="sticky top-0 z-10 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-b">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link href="/" className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors">
              <ArrowLeftIcon className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Link>
          </div>
          <h1 className="text-xl font-semibold absolute left-1/2 transform -translate-x-1/2 flex items-center gap-2">
            <Sparkles className="h-5 w-5 text-primary" />
            Investment Assistant
          </h1>
          <ThemeToggle />
        </div>
      </header>

      {/* Scrollable Chat Area */}
      <main className="flex-1 container mx-auto px-4 py-8 max-w-3xl">
        <ScrollArea ref={scrollAreaRef} className="h-[calc(100vh-200px)] overflow-y-auto">
          <AnimatePresence>
            {messages.map((message) => (
              <motion.div
                key={message.id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -20 }}
                transition={{ duration: 0.3 }}
                className={cn(
                  'flex gap-3 mb-4',
                  message.role === 'user' ? 'flex-row-reverse' : 'flex-row'
                )}
              >
                <div
                  className={cn(
                    'w-8 h-8 rounded-full flex items-center justify-center shrink-0 shadow-sm',
                    message.role === 'assistant'
                      ? 'bg-blue-500 text-white'
                      : 'bg-gray-200 dark:bg-gray-700'
                  )}
                >
                  {message.role === 'assistant' ? (
                    <BotIcon className="h-4 w-4" />
                  ) : (
                    <UserIcon className="h-4 w-4" />
                  )}
                </div>
                <div
                  className={cn(
                    'rounded-lg p-4 max-w-[80%] shadow-sm',
                    message.role === 'assistant'
                      ? 'bg-white dark:bg-gray-800'
                      : 'bg-blue-500 text-white'
                  )}
                >
                  <p className="text-sm">{message.content}</p>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {isTyping && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.3 }}
              className="flex gap-3 items-start mb-4"
            >
              <div className="w-8 h-8 rounded-full flex items-center justify-center bg-blue-500 text-white shadow-sm">
                <BotIcon className="h-4 w-4" />
              </div>
              <div className="bg-white dark:bg-gray-800 rounded-lg p-4 flex gap-1 max-w-[80%] shadow-sm">
                <span className="w-2 h-2 bg-current rounded-full animate-bounce" />
                <span className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
                <span className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.4s]" />
              </div>
            </motion.div>
          )}
        </ScrollArea>
      </main>

      {/* Fixed Input Area */}
      <div className="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 backdrop-blur-md border-t">
        <div className="container mx-auto px-4 py-4 max-w-3xl">
          <div className="flex gap-2">
            <Input
              ref={inputRef}
              placeholder="Type your message..."
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              className="flex-1 bg-white dark:bg-gray-800 shadow-sm"
            />
            <Button 
              onClick={handleSend}
              className="bg-blue-500 hover:bg-blue-600 text-white shadow-sm transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
              disabled={isTyping || !input.trim()}
            >
              <SendIcon className="h-4 w-4" />
            </Button>
          </div>
        </div>
      </div>
    </div>
  );
}