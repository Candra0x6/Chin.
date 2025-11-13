'use client';

import React, { useState } from 'react';
import { usePathname, useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { Card, CardContent } from './ui/card';
import { Alert, AlertDescription } from './ui/alert';
import ChatAssistant from './ChatAssistant';

type NavItem = 'home' | 'visual' | 'settings' | 'history' | 'analytics';

export default function Dashboard({children} : {children: React.ReactNode}) {
  const router = useRouter();
  const analysis_id = localStorage.getItem('analysisId');
  const [expandedCard, setExpandedCard] = useState<string | null>(null);
 const path = usePathname();
  // Navigation items
  const navItems: Array<{ id: NavItem; icon: string; label: string; route: string }> = [
    { id: 'home', icon: '🏠', label: 'Home', route: '/dashboard' },
    { id: 'visual', icon: '👁️', label: 'Visual', route: '/dashboard/visual' },
    { id: 'analytics', icon: '📊', label: 'Analytics', route: '/dashboard/analytics' },
  ];

  const header : () => { title: string; subtitle: string } = (() => {
    switch (path) {
      case '/dashboard':  
        return { title: 'Dashboard', subtitle: 'Overview of emergency room status' };
      case '/dashboard/visual':
        return { title: '3D Visualizer', subtitle: 'Visual representation 3D emergency room' };
      case '/dashboard/analytics':
        return { title: 'Analytics', subtitle: 'Data insights of emergency room usage' };
      default:
        return { title: 'Dashboard', subtitle: '' };
    }
  }   )
  // Handle navigation
  const handleNavigation = (route: string, navId: NavItem) => {
    router.push(route);
  };

  const pathname = usePathname()
  // Animation variants
  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: { staggerChildren: 0.1, delayChildren: 0.1 },
    },
  };

  const itemVariants = {
    hidden: { opacity: 0, y: 20 },
    visible: { opacity: 1, y: 0, transition: { duration: 0.5 } },
  };

  const cardHoverVariants = {
    hover: {
      scale: 1.02,
      boxShadow: '0 20px 40px rgba(0, 0, 0, 0.1)',
      transition: { duration: 0.3 },
    },
  };

  const navItemVariants = {
    idle: { scale: 1 },
    hover: { scale: 1.15, transition: { duration: 0.3 } },
    active: {
      scale: 1.1,
      backgroundColor: 'rgb(17, 24, 39)',
      transition: { duration: 0.3 },
    },
  };

  return (
    <motion.div
      className="min-h-screen bg-linear-to-br from-blue-50 via-white to-purple-50 dark:from-gray-900 dark:via-gray-800 dark:to-gray-900 p-6 transition-colors duration-300"
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      transition={{ duration: 0.5 }}
    >
      <div className="">
        {/* Main container */}
        <motion.div
          className="flex gap-6 min-h-screen"
          variants={containerVariants}
          initial="hidden"
          animate="visible"
        >
          {/* Left Sidebar Navigation bar */}
          <motion.div
            className="w-24 bg-white dark:bg-gray-800 rounded-2xl p-4 flex flex-col items-center gap-8 shadow-lg hover:shadow-xl transition-shadow"
            variants={itemVariants}
          >
            {/* Logo */}
            <motion.div
              className="w-12 h-12 bg-linear-to-br from-purple-400 to-purple-600 rounded-full flex items-center justify-center cursor-pointer"
              whileHover={{ rotate: 360 }}
              whileTap={{ scale: 0.9 }}
              transition={{ duration: 0.5 }}
              onClick={() => handleNavigation('/', 'home')}
            >
              <div className="text-white text-lg font-bold">★</div>
            </motion.div>

            {/* Navigation Items */}
            <div className="flex flex-col gap-6 flex-1">
              {navItems.map((item) => (
                <motion.button
                  key={item.id}
                  className={`w-12 h-12 rounded-full flex items-center justify-center text-lg transition-all ${
                    pathname === item.route
                      ? 'bg-gray-900 dark:bg-white text-white dark:text-gray-900'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                  }`}
                  variants={navItemVariants}
                  whileHover="hover"
                  whileTap={{ scale: 0.95 }}
                  onClick={() => handleNavigation(item.route, item.id)}
                  title={item.label}
                >
                  {item.icon}
                </motion.button>
              ))}
            </div>

            {/* Profile */}
            <motion.div
              className="w-12 h-12 bg-linear-to-br from-purple-400 to-pink-400 rounded-full cursor-pointer"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => handleNavigation('/settings', 'settings')}
              title="Profile Settings"
            />
          </motion.div>

          {/* Center Content */}
          <motion.div
            className="flex-1 flex flex-col gap-6 h-full"
            variants={itemVariants}
          >
            {/* Header */}
            <motion.div
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg flex items-center justify-between"
              variants={cardHoverVariants}
            >
              <motion.div initial={{ x: -20, opacity: 0 }} animate={{ x: 0, opacity: 1 }}>
                <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                  {header().title}
                </h1>
                <p className="text-sm text-gray-600 dark:text-gray-400 mt-1">
                {header().subtitle}
                </p>
              </motion.div>
              <div className="flex gap-3">
                <motion.button
                  className="px-4 py-2 bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 rounded-full font-medium hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  ✏️ Edit
                </motion.button>
                <motion.button
                  className="px-4 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-full font-medium hover:bg-gray-800 dark:hover:bg-gray-100 transition-colors"
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                >
                  + Add device
                </motion.button>
              </div>
            </motion.div>


            {/* 3D View Area */}
            <motion.div
              className="flex-1 flex items-center justify-center h-full"
              variants={itemVariants}
              whileHover="hover"
            >
            {children}
            </motion.div>

       
          </motion.div>

          {/* Right Sidebar - Controls */}
          <motion.div
            className="w-80 flex flex-col gap-4"
            variants={itemVariants}
          >
            {/* Cleaning Card */}

            {/* Bg gray 800 = #1F2937 */}
            <motion.div
              className="bg-white dark:bg-gray-800 rounded-2xl p-6 shadow-lg cursor-pointer h-full"
              variants={cardHoverVariants}
             
            >
              <motion.div className="flex items-center justify-between mb-4">
                <div>
                  <h3 className="font-bold text-gray-900 dark:text-white">
                    AI Chat
                  </h3>
                  <p className="text-xs text-gray-500 dark:text-gray-400">
                    Your AI assistant is here to help!
                  </p>
                </div>
            
              </motion.div>
               {/* Main Content */}
      <main className="">
        <div className="overflow-hidden">
          <div className="p-0">
            <ChatAssistant analysisId={analysis_id as string} />
          </div>
        </div>

        {/* Tips Section */}
        <Alert className="mt-6 bg-purple-50 dark:bg-purple-900/20 border-purple-200 dark:border-purple-800">
          <AlertDescription>
            <h3 className="text-lg font-semibold text-purple-900 dark:text-purple-200 mb-3">
              💡 Tips for Better Conversations
            </h3>
            <ul className="space-y-2 text-sm text-purple-800 dark:text-purple-300">
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Ask specific questions about the analysis results</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Try &ldquo;What if&rdquo; scenarios (e.g., &ldquo;What if we add 2 more nurses?&rdquo;)</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Ask for clarification on bottlenecks and recommendations</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-purple-600 dark:text-purple-400">•</span>
                <span>Request insights on peak hours and crowd patterns</span>
              </li>
            </ul>
          </AlertDescription>
        </Alert>

        {/* Example Questions */}
        <Card className="mt-6">
          <CardContent className="pt-6">
            <h3 className="text-lg font-semibold mb-4">
              Example Questions
            </h3>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
              <Card className="py-0 bg-muted">
                <CardContent className="p-3">
                  <p className="text-sm">
                    &ldquo;When was the crowd highest?&rdquo;
                  </p>
                </CardContent>
              </Card>
              <Card className="py-0 bg-muted">
                <CardContent className="p-3">
                  <p className="text-sm">
                    &ldquo;Why do you recommend 3 nurses?&rdquo;
                  </p>
                </CardContent>
              </Card>
              <Card className="py-0 bg-muted">
                <CardContent className="p-3">
                  <p className="text-sm">
                    &ldquo;What areas had the most congestion?&rdquo;
                  </p>
                </CardContent>
              </Card>
              <Card className="py-0 bg-muted">
                <CardContent className="p-3">
                  <p className="text-sm">
                    &ldquo;How can we reduce wait times?&rdquo;
                  </p>
                </CardContent>
              </Card>
            </div>
          </CardContent>
        </Card>
      </main>
            </motion.div>

          </motion.div>
        </motion.div>
      </div>
    </motion.div>
  );
}
