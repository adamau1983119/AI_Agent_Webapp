/**
 * 打字效果 Hook
 * 用於 AI 回覆的逐字顯示效果
 */
import { useState, useEffect } from 'react';

interface UseTypewriterOptions {
  text: string;
  speed?: number; // 每個字符的延遲時間（毫秒）
  onComplete?: () => void;
}

export function useTypewriter({ text, speed = 30, onComplete }: UseTypewriterOptions) {
  const [displayedText, setDisplayedText] = useState('');
  const [isTyping, setIsTyping] = useState(false);

  useEffect(() => {
    if (!text) {
      setDisplayedText('');
      setIsTyping(false);
      return;
    }

    setIsTyping(true);
    setDisplayedText('');

    let currentIndex = 0;
    const timer = setInterval(() => {
      if (currentIndex < text.length) {
        setDisplayedText(text.slice(0, currentIndex + 1));
        currentIndex++;
      } else {
        clearInterval(timer);
        setIsTyping(false);
        if (onComplete) {
          onComplete();
        }
      }
    }, speed);

    return () => clearInterval(timer);
  }, [text, speed, onComplete]);

  return { displayedText, isTyping };
}

