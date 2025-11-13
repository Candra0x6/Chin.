'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Progress } from '@/components/ui/progress';

export default function DashboardPage() {
  const router = useRouter();
  const [currentTime, setCurrentTime] = useState(new Date());

  useEffect(() => {
    const timer = setInterval(() => setCurrentTime(new Date()), 1000);
    return () => clearInterval(timer);
  }, []);

  // Mock data - replace with actual data from your API
  const stats = {
    totalAnalyses: 24,
    avgCrowdSize: 42.5,
    totalPeople: 1020,
    activeAlerts: 3,
  };

  const recentAnalyses = [
    { id: '1', name: 'Hospital ER - Morning', date: '2025-11-13', status: 'completed', crowdLevel: 'High' },
    { id: '2', name: 'Waiting Room Analysis', date: '2025-11-12', status: 'completed', crowdLevel: 'Medium' },
    { id: '3', name: 'Lobby Monitoring', date: '2025-11-12', status: 'processing', crowdLevel: 'Low' },
  ];

  const quickActions = [
    {
      title: 'New Analysis',
      description: 'Upload video for crowd analysis',
      icon: '📊',
      action: () => router.push('/'),
      color: 'bg-blue-500',
    },
    {
      title: 'View History',
      description: 'Browse past analyses',
      icon: '📁',
      action: () => router.push('/history'),
      color: 'bg-purple-500',
    },
    {
      title: 'AI Chat',
      description: 'Ask questions about results',
      icon: '💬',
      action: () => router.push('/chat/latest'),
      color: 'bg-green-500',
    },
    {
      title: 'Reports',
      description: 'Generate detailed reports',
      icon: '📄',
      action: () => console.log('Reports'),
      color: 'bg-orange-500',
    },
  ];

  const alerts = [
    { type: 'warning', message: 'High crowd density detected in ER - 3 hours ago', priority: 'high' },
    { type: 'info', message: 'New AI insights available for analysis #1234', priority: 'medium' },
    { type: 'success', message: 'System optimization completed successfully', priority: 'low' },
  ];

  const getCrowdLevelColor = (level: string) => {
    switch (level) {
      case 'High': return 'destructive';
      case 'Medium': return 'default';
      case 'Low': return 'secondary';
      default: return 'outline';
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed': return 'text-green-600 dark:text-green-400';
      case 'processing': return 'text-blue-600 dark:text-blue-400';
      case 'failed': return 'text-red-600 dark:text-red-400';
      default: return 'text-gray-600 dark:text-gray-400';
    }
  };

  return (
    <div className="min-h-screen bg-gray-800 p-8 rounded-2xl">
     

      <main className="">
        {/* Stats Overview */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total Analyses
              </CardTitle>
              <div className="w-8 h-8 bg-blue-100 dark:bg-blue-900/30 rounded-full flex items-center justify-center">
                <span className="text-lg">📊</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.totalAnalyses}</div>
              <p className="text-xs text-muted-foreground mt-1">
                +12% from last month
              </p>
              <Progress value={75} className="mt-3" />
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Avg Crowd Size
              </CardTitle>
              <div className="w-8 h-8 bg-purple-100 dark:bg-purple-900/30 rounded-full flex items-center justify-center">
                <span className="text-lg">👥</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.avgCrowdSize}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Average per analysis
              </p>
              <Progress value={60} className="mt-3" />
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Total People
              </CardTitle>
              <div className="w-8 h-8 bg-green-100 dark:bg-green-900/30 rounded-full flex items-center justify-center">
                <span className="text-lg">🚶</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold">{stats.totalPeople}</div>
              <p className="text-xs text-muted-foreground mt-1">
                Detected across all analyses
              </p>
              <Progress value={85} className="mt-3" />
            </CardContent>
          </Card>

          <Card className="hover:shadow-lg transition-shadow border-orange-200 dark:border-orange-800">
            <CardHeader className="flex flex-row items-center justify-between pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Active Alerts
              </CardTitle>
              <div className="w-8 h-8 bg-orange-100 dark:bg-orange-900/30 rounded-full flex items-center justify-center">
                <span className="text-lg">⚠️</span>
              </div>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-orange-600 dark:text-orange-400">
                {stats.activeAlerts}
              </div>
              <p className="text-xs text-muted-foreground mt-1">
                Requires attention
              </p>
              <Progress value={30} className="mt-3 [&>div]:bg-orange-600" />
            </CardContent>
          </Card>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Recent Analyses */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span>📈</span> Recent Analyses
                </CardTitle>
                <CardDescription>
                  Your latest crowd analysis results
                </CardDescription>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {recentAnalyses.map((analysis) => (
                    <Card key={analysis.id} className="py-0 hover:bg-muted/50 transition-colors cursor-pointer" onClick={() => router.push(`/analysis/${analysis.id}`)}>
                      <CardContent className="p-4">
                        <div className="flex items-center justify-between">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <h4 className="font-semibold">{analysis.name}</h4>
                              <Badge variant={getCrowdLevelColor(analysis.crowdLevel)}>
                                {analysis.crowdLevel}
                              </Badge>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-muted-foreground">
                              <span>📅 {analysis.date}</span>
                              <span className={getStatusColor(analysis.status)}>
                                ● {analysis.status}
                              </span>
                            </div>
                          </div>
                          <Button variant="ghost" size="sm">
                            View →
                          </Button>
                        </div>
                      </CardContent>
                    </Card>
                  ))}
                </div>
                <Button variant="outline" className="w-full mt-4" onClick={() => router.push('/history')}>
                  View All Analyses
                </Button>
              </CardContent>
            </Card>

          
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Alerts */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span>🔔</span> Alerts
                </CardTitle>
                <CardDescription>
                  System notifications
                </CardDescription>
              </CardHeader>
              <CardContent className="space-y-3">
                {alerts.map((alert, index) => (
                  <Alert 
                    key={index} 
                    variant={alert.type === 'warning' ? 'destructive' : 'default'}
                    className={
                      alert.type === 'success' ? 'border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20' :
                      alert.type === 'info' ? 'border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20' : ''
                    }
                  >
                    <AlertDescription className="text-xs">
                      {alert.message}
                    </AlertDescription>
                  </Alert>
                ))}
              </CardContent>
            </Card>

            {/* System Status */}
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2">
                  <span>💻</span> System Status
                </CardTitle>
              </CardHeader>
              <CardContent className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">API Status</span>
                    <Badge variant="secondary" className="bg-green-100 dark:bg-green-900/30 text-green-700 dark:text-green-300">
                      ● Online
                    </Badge>
                  </div>
                  <Progress value={100} className="[&>div]:bg-green-600" />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Storage Used</span>
                    <span className="text-sm font-medium">2.4 / 10 GB</span>
                  </div>
                  <Progress value={24} />
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Analysis Queue</span>
                    <span className="text-sm font-medium">0 pending</span>
                  </div>
                  <Progress value={0} />
                </div>
              </CardContent>
            </Card>

            {/* Tips */}
            <Card className="bg-linear-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 border-purple-200 dark:border-purple-800">
              <CardHeader>
                <CardTitle className="flex items-center gap-2 text-purple-900 dark:text-purple-200">
                  <span>💡</span> Pro Tip
                </CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-purple-800 dark:text-purple-300">
                  Use AI Chat to get deeper insights about your analysis results. Ask &quot;What if&quot; scenarios to optimize staffing!
                </p>
                <Button variant="outline" className="w-full mt-3 border-purple-300 dark:border-purple-700" size="sm">
                  Learn More
                </Button>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>
    </div>
  );
}
