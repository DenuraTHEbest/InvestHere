"use client";

import { useState, useRef, useEffect } from 'react';
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Button } from "@/components/ui/button";
import { ScrollArea } from "@/components/ui/scroll-area";
import { ArrowLeftIcon, SendIcon, BotIcon, UserIcon, Sparkles } from "lucide-react";
import { ThemeToggle } from "@/components/theme-toggle";
import Link from 'next/link';

type Message = {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
};

const TYPING_SPEED = 25; // ms per character

export default function ChatPage() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: `👋 Welcome to InvestHere! I'm your AI investment assistant, ready to help you make informed decisions.
    
    I can help you with:
    • Stock price predictions and analysis
    • Market sentiment insights
    • ASPI trends and forecasts
    • Investment strategies and recommendations
    
    What would you like to know about today?`,
      timestamp: new Date(),
    }
  ]);
  const [input, setInput] = useState('');
  const [isTyping, setIsTyping] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const [displayedContent, setDisplayedContent] = useState('');
  const [currentMessageIndex, setCurrentMessageIndex] = useState(0);
  const inputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages, displayedContent]);

  useEffect(() => {
    if (isTyping && currentMessageIndex < messages.length) {
      const content = messages[currentMessageIndex].content;
      let currentIndex = 0;

      const typingInterval = setInterval(() => {
        if (currentIndex <= content.length) {
          setDisplayedContent(content.slice(0, currentIndex));
          currentIndex++;
        } else {
          clearInterval(typingInterval);
          setIsTyping(false);
          setCurrentMessageIndex(prev => prev + 1);
        }
      }, TYPING_SPEED);

      return () => clearInterval(typingInterval);
    }
  }, [isTyping, currentMessageIndex, messages]);

  const handleSend = () => {
    if (!input.trim()) return;

    // Add user message
    setMessages(prev => [...prev, { 
      role: 'user', 
      content: input,
      timestamp: new Date(),
    }]);
    setInput('');
    setIsTyping(true);

    // Simulate AI response (replace with actual API call)
    setTimeout(() => {
      setIsTyping(false);
      setMessages(prev => [...prev, {
        role: 'assistant',
        content: 'I understand you\'re interested in market insights. Based on our analysis, the current market sentiment is positive, with a predicted ASPI increase of 2.34% tomorrow. Would you like more specific information about any particular stocks?',
        timestamp: new Date(),
      }]);
    }, 1000);
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <header className="border-b sticky top-0 z-10 bg-background">
        <div className="container mx-auto px-4 py-4 flex items-center justify-between">
          <div className="flex items-center gap-4">
            <Link 
              href="/" 
              className="flex items-center gap-2 text-muted-foreground hover:text-foreground transition-colors"
            >
              <ArrowLeftIcon className="h-4 w-4" />
              <span>Back to Dashboard</span>
            </Link>
            <h1 className="text-xl font-semibold absolute left-1/2 transform -translate-x-1/2 flex items-center gap-2">
              <Sparkles className ="h-5 w-5 text-primary" />
              Investment Assistant
              </h1>
          </div>
          <ThemeToggle />
        </div>
      </header>

      <main className="flex-1 container mx-auto px-4 py-8 flex flex-col max-w-3xl">
        <Card className="flex-1 flex flex-col min-h-[600px] shadow-lg">
          <ScrollArea 
            ref={scrollAreaRef}
            className="flex-1 p-4 space-y-4"
          >
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex gap-3 ${
                  message.role === 'assistant' ? 'items-start' : 'items-start flex-row-reverse'
                } ${index === messages.length - 1 ? 'animate-in slide-in-from-bottom-2' : ''} duration-300`}
              >
                <div 
                  className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 
                    ${message.role === 'assistant' 
                      ? 'bg-primary text-primary-foreground shadow-inner' 
                      : 'bg-muted shadow-sm'
                    }`}
                >
                  {message.role === 'assistant' ? (
                    <BotIcon className="h-4 w-4" />
                  ) : (
                    <UserIcon className="h-4 w-4" />
                  )}
                </div>
                <div className="flex flex-col gap-1 max-w-[80%]">
                  <div className={`rounded-lg p-4 ${
                    message.role === 'assistant' 
                      ? 'bg-muted' 
                      : 'bg-primary text-primary-foreground'
                  }`}>
                    {message.content}
                  </div>
                  <span className="text-xs text-muted-foreground px-1">
                    {message.timestamp.toLocaleTimeString()}
                  </span>
                </div>
              </div>
            ))}
            {isTyping && (
              <div className="flex gap-3 items-start">
                <div className="w-8 h-8 rounded-full flex items-center justify-center bg-primary text-primary-foreground">
                  <BotIcon className="h-4 w-4" />
                </div>
                <div className="bg-muted rounded-lg p-4 flex gap-1 max-w-[80%]">
                  <span className="w-2 h-2 bg-current rounded-full animate-bounce" />
                  <span className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.2s]" />
                  <span className="w-2 h-2 bg-current rounded-full animate-bounce [animation-delay:0.4s]" />
                </div>
              </div>
            )}
          </ScrollArea>
          
          <div className="p-4 border-t">
            <div className="flex gap-2">
              <Input
                placeholder="Type your message..."
                value={input}
                onChange={(e) => setInput(e.target.value)}
                onKeyPress={handleKeyPress}
                className="flex-1"
              />
              <Button 
                onClick={handleSend}
                className="shadow-sm transition-all hover:scale-105 active:scale-95 disabled:opacity-50"
                disabled={isTyping || !input.trim()}
              >
                <SendIcon className="h-4 w-4" />
              </Button>
            </div>
          </div>
        </Card>
      </main>
    </div>
  );
}