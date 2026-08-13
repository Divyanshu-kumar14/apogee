import { motion } from 'framer-motion'

/**
 * AnimatedBackground - Animated gradient background for the app
 * Features:
 * - Smooth gradient animation
 * - CSS-based (lightweight, no WebGL)
 * - Subtle and non-distracting
 * - Can be upgraded to WebGL shader later
 */
export default function AnimatedBackground() {
  return (
    <motion.div
      className="fixed inset-0 -z-10 animated-gradient"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 1 }}
    />
  )
}

/**
 * Alternative: Mesh Gradient Background (more subtle)
 */
export function MeshGradientBackground() {
  return (
    <div className="fixed inset-0 -z-10 overflow-hidden">
      <motion.div
        className="absolute inset-0 opacity-30"
        style={{
          background: `
            radial-gradient(at 0% 0%, rgba(30, 58, 138, 0.3) 0px, transparent 50%),
            radial-gradient(at 100% 0%, rgba(59, 130, 246, 0.3) 0px, transparent 50%),
            radial-gradient(at 100% 100%, rgba(139, 92, 246, 0.3) 0px, transparent 50%),
            radial-gradient(at 0% 100%, rgba(236, 72, 153, 0.3) 0px, transparent 50%)
          `
        }}
        initial={{ opacity: 0 }}
        animate={{ opacity: 0.3 }}
        transition={{ duration: 1.5 }}
      />
    </div>
  )
}

/**
 * Subtle gradient overlay for glass cards
 */
export function GradientOverlay({ className = '' }) {
  return (
    <div 
      className={`absolute inset-0 bg-gradient-to-br from-white/5 to-transparent pointer-events-none ${className}`}
    />
  )
}
