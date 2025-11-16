/**
 * Framer Motion Animation Variants
 *
 * Reusable animation configurations for consistent UI interactions
 */

import { Variants } from 'framer-motion';

/**
 * Page transition animations
 * Used with AnimatePresence for route changes
 */
export const pageVariants: Variants = {
  initial: {
    opacity: 0,
    y: 20,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  exit: {
    opacity: 0,
    y: -20,
    transition: {
      duration: 0.3,
      ease: 'easeIn',
    },
  },
};

/**
 * Stagger container for lists/grids
 * Children animate in sequence
 */
export const staggerContainer: Variants = {
  initial: {},
  animate: {
    transition: {
      staggerChildren: 0.1,
      delayChildren: 0.1,
    },
  },
};

/**
 * Stagger item for card animations
 * Used inside staggerContainer
 */
export const staggerItem: Variants = {
  initial: {
    opacity: 0,
    y: 30,
    scale: 0.95,
  },
  animate: {
    opacity: 1,
    y: 0,
    scale: 1,
    transition: {
      duration: 0.5,
      ease: [0.25, 0.1, 0.25, 1], // Custom easing
    },
  },
};

/**
 * Image fade-in animation
 * Smooth loading effect
 */
export const imageFadeIn: Variants = {
  initial: {
    opacity: 0,
    scale: 1.05,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Button tap animation
 * Provides tactile feedback
 */
export const buttonTap = {
  scale: 0.95,
  transition: {
    duration: 0.1,
    ease: 'easeInOut',
  },
};

/**
 * Button hover animation
 * Subtle lift effect
 */
export const buttonHover = {
  scale: 1.02,
  transition: {
    duration: 0.2,
    ease: 'easeOut',
  },
};

/**
 * Card hover animation
 * Lift and shadow effect
 */
export const cardHover = {
  y: -4,
  scale: 1.01,
  transition: {
    duration: 0.3,
    ease: 'easeOut',
  },
};

/**
 * Fade in from bottom
 * Used with Intersection Observer
 */
export const fadeInUp: Variants = {
  initial: {
    opacity: 0,
    y: 40,
  },
  animate: {
    opacity: 1,
    y: 0,
    transition: {
      duration: 0.6,
      ease: 'easeOut',
    },
  },
};

/**
 * Scale in animation
 * Pop effect
 */
export const scaleIn: Variants = {
  initial: {
    opacity: 0,
    scale: 0.8,
  },
  animate: {
    opacity: 1,
    scale: 1,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
};

/**
 * Slide in from right
 * Drawer/modal animation
 */
export const slideInRight: Variants = {
  initial: {
    x: '100%',
    opacity: 0,
  },
  animate: {
    x: 0,
    opacity: 1,
    transition: {
      duration: 0.4,
      ease: 'easeOut',
    },
  },
  exit: {
    x: '100%',
    opacity: 0,
    transition: {
      duration: 0.3,
      ease: 'easeIn',
    },
  },
};

/**
 * Modal backdrop animation
 */
export const backdropVariants: Variants = {
  initial: {
    opacity: 0,
  },
  animate: {
    opacity: 1,
    transition: {
      duration: 0.2,
    },
  },
  exit: {
    opacity: 0,
    transition: {
      duration: 0.2,
    },
  },
};

/**
 * Skeleton pulse animation
 * Used for loading states
 */
export const skeletonPulse = {
  opacity: [0.6, 1, 0.6],
  transition: {
    duration: 1.5,
    repeat: Infinity,
    ease: 'easeInOut',
  },
};
