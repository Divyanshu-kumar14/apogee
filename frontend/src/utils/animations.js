/**
 * Framer Motion animation variants for consistent animations across the app
 * These variants use spring physics for natural, weighted movement
 */

// Card animations with glass morphism effects
export const cardVariants = {
  hidden: { 
    opacity: 0, 
    y: 20,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    y: 0,
    scale: 1,
    transition: { 
      type: 'spring', 
      stiffness: 300, 
      damping: 20,
      mass: 0.8
    }
  },
  hover: { 
    scale: 1.02, 
    y: -4,
    transition: { 
      type: 'spring', 
      stiffness: 400, 
      damping: 10 
    }
  },
  tap: {
    scale: 0.98
  }
}

// List container animations with stagger effect
export const listVariants = {
  hidden: { 
    opacity: 0 
  },
  visible: {
    opacity: 1,
    transition: { 
      staggerChildren: 0.1,
      delayChildren: 0.2
    }
  }
}

// Individual list item animations
export const itemVariants = {
  hidden: { 
    opacity: 0, 
    x: -20,
    scale: 0.95
  },
  visible: { 
    opacity: 1, 
    x: 0,
    scale: 1,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 25
    }
  },
  exit: {
    opacity: 0,
    x: 20,
    scale: 0.95,
    transition: {
      duration: 0.2
    }
  }
}

// Tab switching animations
export const tabVariants = {
  enter: (direction) => ({
    x: direction > 0 ? 20 : -20,
    opacity: 0
  }),
  center: {
    x: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30
    }
  },
  exit: (direction) => ({
    x: direction < 0 ? 20 : -20,
    opacity: 0,
    transition: {
      duration: 0.2
    }
  })
}

// Modal/Dialog animations
export const modalVariants = {
  hidden: {
    opacity: 0,
    scale: 0.95,
    y: 20
  },
  visible: {
    opacity: 1,
    scale: 1,
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 25
    }
  },
  exit: {
    opacity: 0,
    scale: 0.95,
    y: 20,
    transition: {
      duration: 0.2
    }
  }
}

// Backdrop overlay animations
export const backdropVariants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.3
    }
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2
    }
  }
}

// Pulse animation for critical alerts
export const pulseVariants = {
  initial: {
    scale: 1,
    boxShadow: '0 0 0 0 rgba(239, 68, 68, 0.7)'
  },
  animate: {
    scale: [1, 1.05, 1],
    boxShadow: [
      '0 0 0 0 rgba(239, 68, 68, 0.7)',
      '0 0 0 10px rgba(239, 68, 68, 0)',
      '0 0 0 0 rgba(239, 68, 68, 0)'
    ],
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'easeInOut'
    }
  }
}

// Fade in animation for page loads
export const fadeInVariants = {
  hidden: {
    opacity: 0
  },
  visible: {
    opacity: 1,
    transition: {
      duration: 0.5,
      ease: 'easeOut'
    }
  }
}

// Slide in from bottom (for notifications)
export const slideUpVariants = {
  hidden: {
    y: 100,
    opacity: 0
  },
  visible: {
    y: 0,
    opacity: 1,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 30
    }
  },
  exit: {
    y: 100,
    opacity: 0,
    transition: {
      duration: 0.2
    }
  }
}

// Number counting animation helper
export const numberCountVariants = {
  hidden: { opacity: 0, y: 20 },
  visible: { 
    opacity: 1, 
    y: 0,
    transition: {
      type: 'spring',
      stiffness: 300,
      damping: 20
    }
  }
}

// Skeleton loading shimmer effect
export const shimmerVariants = {
  initial: {
    backgroundPosition: '-200% 0'
  },
  animate: {
    backgroundPosition: '200% 0',
    transition: {
      duration: 2,
      repeat: Infinity,
      ease: 'linear'
    }
  }
}

// Spring configuration presets
export const springConfigs = {
  gentle: {
    type: 'spring',
    stiffness: 200,
    damping: 20
  },
  snappy: {
    type: 'spring',
    stiffness: 400,
    damping: 25
  },
  bouncy: {
    type: 'spring',
    stiffness: 300,
    damping: 10
  },
  slow: {
    type: 'spring',
    stiffness: 100,
    damping: 20
  }
}

// Transition presets
export const transitions = {
  fast: { duration: 0.2 },
  normal: { duration: 0.3 },
  slow: { duration: 0.5 }
}
