import { useEffect, useRef, useState, useCallback } from 'react';

/**
 * Custom WebSocket hook with automatic reconnection and exponential backoff
 * 
 * Features:
 * - Automatic reconnection with exponential backoff
 * - Connection state management
 * - Message throttling support
 * - Cleanup on unmount
 * 
 * @param {string} url - WebSocket URL
 * @param {Object} options - Configuration options
 * @param {number} options.reconnectInterval - Initial reconnect delay in ms (default: 1000)
 * @param {number} options.maxReconnectAttempts - Max reconnection attempts (default: 5)
 * @param {Function} options.onMessage - Message handler callback
 * @param {Function} options.onError - Error handler callback
 * @param {Function} options.onOpen - Connection open callback
 * @param {Function} options.onClose - Connection close callback
 * @returns {Object} { isConnected, send, close }
 */
export function useWebSocket(url, options = {}) {
  const {
    reconnectInterval = 1000,
    maxReconnectAttempts = 5,
    onMessage,
    onError,
    onOpen,
    onClose
  } = options;

  const [isConnected, setIsConnected] = useState(false);
  const wsRef = useRef(null);
  const reconnectTimeoutRef = useRef(null);
  const shouldReconnectRef = useRef(true);
  const reconnectCountRef = useRef(0);
  const urlRef = useRef(url);

  // Update URL ref when it changes
  useEffect(() => {
    urlRef.current = url;
  }, [url]);

  const connect = useCallback(() => {
    // Don't connect if already connected or shouldn't reconnect
    if (wsRef.current?.readyState === WebSocket.OPEN || !shouldReconnectRef.current) {
      return;
    }

    // Clear any existing connection
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    try {
      const ws = new WebSocket(urlRef.current);
      wsRef.current = ws;

      ws.onopen = () => {
        console.log('[WebSocket] Connected to', urlRef.current);
        setIsConnected(true);
        reconnectCountRef.current = 0;
        onOpen?.();
      };

      ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          onMessage?.(data);
        } catch (err) {
          console.error('[WebSocket] Failed to parse message:', err);
          onError?.(err);
        }
      };

      ws.onerror = (error) => {
        console.error('[WebSocket] Error:', error);
        onError?.(error);
      };

      ws.onclose = (event) => {
        console.log('[WebSocket] Disconnected:', event.code, event.reason);
        setIsConnected(false);
        wsRef.current = null;
        onClose?.(event);

        // Attempt reconnection with exponential backoff
        if (shouldReconnectRef.current && reconnectCountRef.current < maxReconnectAttempts) {
          const delay = Math.min(
            reconnectInterval * Math.pow(2, reconnectCountRef.current),
            30000 // Max 30 seconds
          );
          
          console.log(`[WebSocket] Reconnecting in ${delay}ms (attempt ${reconnectCountRef.current + 1}/${maxReconnectAttempts})`);
          
          reconnectTimeoutRef.current = setTimeout(() => {
            reconnectCountRef.current += 1;
            connect();
          }, delay);
        } else if (reconnectCountRef.current >= maxReconnectAttempts) {
          console.error('[WebSocket] Max reconnection attempts reached');
        }
      };
    } catch (err) {
      console.error('[WebSocket] Connection error:', err);
      onError?.(err);
    }
  }, [reconnectInterval, maxReconnectAttempts, onMessage, onError, onOpen, onClose]);

  useEffect(() => {
    shouldReconnectRef.current = true;
    reconnectCountRef.current = 0;
    connect();

    return () => {
      // Cleanup on unmount
      shouldReconnectRef.current = false;
      
      if (reconnectTimeoutRef.current) {
        clearTimeout(reconnectTimeoutRef.current);
      }
      
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
  }, [connect]);

  const send = useCallback((data) => {
    if (wsRef.current?.readyState === WebSocket.OPEN) {
      try {
        wsRef.current.send(typeof data === 'string' ? data : JSON.stringify(data));
      } catch (err) {
        console.error('[WebSocket] Failed to send message:', err);
        onError?.(err);
      }
    } else {
      console.warn('[WebSocket] Cannot send message - not connected');
    }
  }, [onError]);

  const close = useCallback(() => {
    shouldReconnectRef.current = false;
    if (reconnectTimeoutRef.current) {
      clearTimeout(reconnectTimeoutRef.current);
    }
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }
  }, []);

  return { isConnected, send, close };
}

/**
 * Throttle function to limit execution rate
 * @param {Function} func - Function to throttle
 * @param {number} limit - Minimum time between executions in ms
 * @returns {Function} Throttled function
 */
export function throttle(func, limit) {
  let inThrottle;
  return function(...args) {
    if (!inThrottle) {
      func.apply(this, args);
      inThrottle = true;
      setTimeout(() => inThrottle = false, limit);
    }
  };
}