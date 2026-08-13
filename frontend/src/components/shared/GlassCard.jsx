import { motion } from 'framer-motion'
import { cn } from '../../utils/cn'
import { cardVariants } from '../../utils/animations'

/**
 * GlassCard - Reusable liquid-glass morphism card component
 * Features:
 * - Backdrop blur effect for depth
 * - Subtle gradient borders
 * - Smooth hover animations with spring physics
 * - Customizable variants (light/dark)
 * - Optional glow effect for critical states
 */
export default function GlassCard({
  children,
  className,
  variant = 'light',
  glow = false,
  glowColor = 'blue',
  hover = true,
  onClick,
  ...props
}) {
  const baseClasses = cn(
    // Base glass effect
    'rounded-xl border backdrop-blur-xl backdrop-saturate-180',
    'shadow-lg transition-shadow duration-300',
    
    // Variant-specific styles
    variant === 'light' && [
      'bg-white/70 border-white/30',
      'shadow-[0_8px_32px_0_rgba(31,38,135,0.15)]'
    ],
    variant === 'dark' && [
      'bg-gray-900/75 border-white/10',
      'shadow-[0_8px_32px_0_rgba(0,0,0,0.3)]'
    ],
    
    // Glow effect for critical states
    glow && [
      glowColor === 'blue' && 'ring-2 ring-blue-500/50',
      glowColor === 'red' && 'ring-2 ring-red-500/50',
      glowColor === 'yellow' && 'ring-2 ring-yellow-500/50',
      glowColor === 'green' && 'ring-2 ring-green-500/50',
      glowColor === 'purple' && 'ring-2 ring-purple-500/50'
    ],
    
    // Hover cursor
    onClick && 'cursor-pointer',
    
    className
  )

  return (
    <motion.div
      className={baseClasses}
      variants={cardVariants}
      initial="hidden"
      animate="visible"
      whileHover={hover ? "hover" : undefined}
      whileTap={onClick ? "tap" : undefined}
      onClick={onClick}
      {...props}
    >
      {children}
    </motion.div>
  )
}

/**
 * GlassCardHeader - Header section for glass cards
 */
export function GlassCardHeader({ children, className }) {
  return (
    <div className={cn('px-6 py-4 border-b border-white/10', className)}>
      {children}
    </div>
  )
}

/**
 * GlassCardBody - Body section for glass cards
 */
export function GlassCardBody({ children, className }) {
  return (
    <div className={cn('px-6 py-4', className)}>
      {children}
    </div>
  )
}

/**
 * GlassCardFooter - Footer section for glass cards
 */
export function GlassCardFooter({ children, className }) {
  return (
    <div className={cn('px-6 py-4 border-t border-white/10', className)}>
      {children}
    </div>
  )
}
