'use client';

import { useState, useEffect } from 'react';
import { 
  LayoutDashboard, 
  Video, 
  Upload, 
  Settings, 
  Bell, 
  Search, 
  Plus, 
  ArrowRight,
  Activity,
  BarChart2,
  Users,
  PlayCircle
} from 'lucide-react';
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer,
  BarChart,
  Bar
} from 'recharts';

// Types for API data
interface Account {
  id: number;
  platform: string;
  username: string;
  status: 'Active' | 'Inactive';
  posts: number;
  views: number;
  engagement: number;
}

interface VideoData {
  id: string;
  title: string;
  views: number;
  likes: number;
  shares: number;
}

interface AnalyticsData {
  name: string;
  views: number;
  likes: number;
  comments: number;
}

interface AnalyticsSummary {
  total_views: number;
  total_likes: number;
  total_comments: number;
  video_count: number;
}

const DashboardPage = () => {
  const [activeTab, setActiveTab] = useState('dashboard');
  const [loading, setLoading] = useState(true);
  const [accounts, setAccounts] = useState<Account[]>([]);
  const [videos, setVideos] = useState<VideoData[]>([]);
  const [analyticsData, setAnalyticsData] = useState<AnalyticsData[]>([]);
  const [analyticsSummary, setAnalyticsSummary] = useState<AnalyticsSummary>({
    total_views: 0,
    total_likes: 0,
    total_comments: 0,
    video_count: 0
  });

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch accounts
        const accountsResponse = await fetch('/api/accounts');
        if (accountsResponse.ok) {
          const accountsData = await accountsResponse.json();
          setAccounts(accountsData.accounts);
        }

        // Fetch analytics summary
        const analyticsResponse = await fetch('/api/analytics');
        if (analyticsResponse.ok) {
          const analyticsData = await analyticsResponse.json();
          setAnalyticsSummary(analyticsData.data);
        }

        // Fetch videos
        const videosResponse = await fetch('/api/videos');
        if (videosResponse.ok) {
          const videosData = await videosResponse.json();
          setVideos(videosData.videos.map((video: any) => ({
            id: video.filename,
            title: video.filename.split('.')[0],
            views: 0,
            likes: 0,
            shares: 0
          })));
        }

        // Generate mock analytics data for chart (we'll replace this with real data later)
        const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
        const generatedData = days.map(day => ({
          name: day,
          views: Math.floor(Math.random() * 5000),
          likes: Math.floor(Math.random() * 2000),
          comments: Math.floor(Math.random() * 200)
        }));
        setAnalyticsData(generatedData);

      } catch (error) {
        console.error('Error fetching data:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gray-50">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary mx-auto mb-4"></div>
          <h2 className="text-xl font-semibold text-gray-900 mb-2">Loading...</h2>
          <p className="text-gray-600">Initializing Opus Dashboard</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <div className="fixed inset-y-0 left-0 w-64 bg-white border-r border-gray-200 z-50">
        <div className="p-6">
          <div className="flex items-center gap-3 mb-8">
            <div className="w-10 h-10 bg-gradient-primary rounded-lg flex items-center justify-center">
              <Video className="w-5 h-5 text-white" />
            </div>
            <h1 className="text-xl font-bold text-gray-900">Opus</h1>
          </div>

          <nav className="space-y-2">
            <button 
              onClick={() => setActiveTab('dashboard')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === 'dashboard' 
                  ? 'bg-blue-50 text-primary font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <LayoutDashboard className="w-5 h-5" />
              <span>Dashboard</span>
            </button>
            
            <button 
              onClick={() => setActiveTab('videos')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === 'videos' 
                  ? 'bg-blue-50 text-primary font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Video className="w-5 h-5" />
              <span>Videos</span>
            </button>
            
            <button 
              onClick={() => setActiveTab('upload')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === 'upload' 
                  ? 'bg-blue-50 text-primary font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Upload className="w-5 h-5" />
              <span>Upload</span>
            </button>
            
            <button 
              onClick={() => setActiveTab('analytics')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === 'analytics' 
                  ? 'bg-blue-50 text-primary font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <BarChart2 className="w-5 h-5" />
              <span>Analytics</span>
            </button>
            
            <button 
              onClick={() => setActiveTab('accounts')}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-lg transition-all ${
                activeTab === 'accounts' 
                  ? 'bg-blue-50 text-primary font-medium' 
                  : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
              }`}
            >
              <Users className="w-5 h-5" />
              <span>Accounts</span>
            </button>
          </nav>
        </div>

        <div className="absolute bottom-6 left-6 right-6">
          <button className="w-full flex items-center gap-3 px-4 py-3 rounded-lg text-gray-600 hover:bg-gray-50 transition-all">
            <Settings className="w-5 h-5" />
            <span>Settings</span>
          </button>
        </div>
      </div>

      {/* Main Content */}
      <div className="ml-64">
        {/* Header */}
        <header className="bg-white border-b border-gray-200 sticky top-0 z-40">
          <div className="px-8 py-4 flex items-center justify-between">
            <div className="flex items-center gap-4">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-gray-400" />
                <input 
                  type="text" 
                  placeholder="Search videos..." 
                  className="pl-10 pr-4 py-2 bg-gray-50 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary w-64"
                />
              </div>
            </div>

            <div className="flex items-center gap-4">
              <button className="relative p-2 text-gray-600 hover:text-gray-900 transition-colors">
                <Bell className="w-5 h-5" />
                <span className="absolute top-2 right-2 w-2 h-2 bg-red-500 rounded-full"></span>
              </button>
              
              <div className="flex items-center gap-3">
                <div className="text-right hidden sm:block">
                  <div className="text-sm font-medium text-gray-900">Admin User</div>
                  <div className="text-xs text-gray-500">Pro Plan</div>
                </div>
                <div className="w-10 h-10 bg-gradient-primary rounded-full flex items-center justify-center text-white font-medium">
                  A
                </div>
              </div>
            </div>
          </div>
        </header>

        {/* Dashboard Content */}
        <main className="px-8 py-8">
          {activeTab === 'dashboard' && (
            <div className="space-y-8">
              {/* Stats Cards */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-primary">
                      <PlayCircle className="w-6 h-6" />
                    </div>
                    <span className="text-green-500 text-sm font-medium">+{Math.floor(Math.random() * 20)}%</span>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {Math.floor(analyticsSummary.total_views / 1000)}.{Math.floor((analyticsSummary.total_views % 1000) / 100)}K
                    </div>
                    <div className="text-gray-500 text-sm">Total Views</div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-green-600">
                      <Activity className="w-6 h-6" />
                    </div>
                    <span className="text-green-500 text-sm font-medium">+{Math.floor(Math.random() * 20)}%</span>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {Math.floor(analyticsSummary.total_likes / 1000)}.{Math.floor((analyticsSummary.total_likes % 1000) / 100)}K
                    </div>
                    <div className="text-gray-500 text-sm">Total Likes</div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                      <BarChart2 className="w-6 h-6" />
                    </div>
                    <span className="text-green-500 text-sm font-medium">+{Math.floor(Math.random() * 10)}%</span>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">{analyticsSummary.video_count}</div>
                    <div className="text-gray-500 text-sm">Videos Uploaded</div>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-4">
                    <div className="w-12 h-12 bg-yellow-100 rounded-lg flex items-center justify-center text-yellow-600">
                      <Users className="w-6 h-6" />
                    </div>
                    <span className="text-green-500 text-sm font-medium">+{Math.floor(Math.random() * 5)}%</span>
                  </div>
                  <div>
                    <div className="text-2xl font-bold text-gray-900 mb-1">
                      {accounts.filter(account => account.status === 'Active').length}
                    </div>
                    <div className="text-gray-500 text-sm">Active Accounts</div>
                  </div>
                </div>
              </div>

              {/* Analytics Charts */}
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Views Over Time</h3>
                    <select className="text-sm border border-gray-200 rounded-lg px-3 py-1 focus:outline-none focus:ring-2 focus:ring-primary">
                      <option>Last 7 Days</option>
                      <option>Last 30 Days</option>
                      <option>Last 3 Months</option>
                    </select>
                  </div>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analyticsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                        <YAxis stroke="#6b7280" fontSize={12} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                          }} 
                        />
                        <Line type="monotone" dataKey="views" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <div className="flex items-center justify-between mb-6">
                    <h3 className="text-lg font-semibold text-gray-900">Top Videos</h3>
                    <button className="text-primary text-sm font-medium flex items-center gap-1">
                      View All <ArrowRight className="w-4 h-4" />
                    </button>
                  </div>
                  <div className="space-y-4">
                    {videos.slice(0, 4).map((video, index) => (
                      <div key={video.id} className="flex items-center gap-4 p-3 rounded-lg hover:bg-gray-50 transition-colors">
                        <div className="w-3 h-3 rounded-full bg-primary"></div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900 truncate">{video.title}</div>
                          <div className="text-sm text-gray-500">{video.views.toLocaleString()} views</div>
                        </div>
                        <div className="text-right">
                          <div className="font-medium text-gray-900">{video.likes.toLocaleString()}</div>
                          <div className="text-xs text-gray-500">Likes</div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* Recent Activity */}
              <div className="bg-white rounded-xl p-6 border border-gray-200">
                <div className="flex items-center justify-between mb-6">
                  <h3 className="text-lg font-semibold text-gray-900">Recent Activity</h3>
                  <button className="text-primary text-sm font-medium flex items-center gap-1">
                    View All <ArrowRight className="w-4 h-4" />
                  </button>
                </div>
                
                <div className="space-y-6">
                  <div className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="w-12 h-12 bg-blue-100 rounded-lg flex items-center justify-center text-primary">
                      <Upload className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Video processed successfully</div>
                      <div className="text-sm text-gray-500">Video #123 was processed and rendered</div>
                    </div>
                    <div className="text-sm text-gray-500">2 hours ago</div>
                  </div>

                  <div className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="w-12 h-12 bg-green-100 rounded-lg flex items-center justify-center text-green-600">
                      <PlayCircle className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Video uploaded to TikTok</div>
                      <div className="text-sm text-gray-500">Video #456 was uploaded to @user1 account</div>
                    </div>
                    <div className="text-sm text-gray-500">5 hours ago</div>
                  </div>

                  <div className="flex items-center gap-4 p-4 rounded-lg hover:bg-gray-50 transition-colors">
                    <div className="w-12 h-12 bg-purple-100 rounded-lg flex items-center justify-center text-purple-600">
                      <BarChart2 className="w-6 h-6" />
                    </div>
                    <div className="flex-1">
                      <div className="font-medium text-gray-900">Analytics report generated</div>
                      <div className="text-sm text-gray-500">Daily analytics report ready</div>
                    </div>
                    <div className="text-sm text-gray-500">1 day ago</div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Videos Section */}
          {activeTab === 'videos' && (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Videos</h2>
                <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Video
                </button>
              </div>

              {/* Video Gallery */}
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {[1, 2, 3, 4, 5, 6].map((video) => (
                  <div key={video} className="bg-white rounded-xl overflow-hidden border border-gray-200">
                    <div className="relative">
                      <div className="aspect-[9/16] bg-gray-200"></div>
                      <div className="absolute inset-0 flex items-center justify-center">
                        <div className="w-16 h-16 bg-black bg-opacity-50 rounded-full flex items-center justify-center">
                          <PlayCircle className="w-8 h-8 text-white" />
                        </div>
                      </div>
                      <div className="absolute bottom-2 right-2 bg-black bg-opacity-70 text-white px-2 py-1 rounded text-xs">
                        0:35
                      </div>
                    </div>
                    <div className="p-4">
                      <div className="font-medium text-gray-900 mb-2">Video Title {video}</div>
                      <div className="text-sm text-gray-500 mb-4">Uploaded 2 days ago</div>
                      <div className="flex items-center justify-between text-sm text-gray-600">
                        <span>1.2K views</span>
                        <span>85 likes</span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Upload Section */}
          {activeTab === 'upload' && (
            <div className="space-y-8">
              <h2 className="text-2xl font-bold text-gray-900">Upload Video</h2>

              <div className="bg-white rounded-xl p-8 border border-gray-200">
                <div className="text-center mb-8">
                  <div className="w-16 h-16 bg-gray-100 rounded-full flex items-center justify-center mx-auto mb-4">
                    <Upload className="w-8 h-8 text-gray-600" />
                  </div>
                  <h3 className="text-lg font-medium text-gray-900 mb-2">Drop your video here</h3>
                  <p className="text-gray-500 mb-6">or click to browse (MP4, MOV, AVI)</p>
                  
                  <div className="max-w-md mx-auto">
                    <input type="file" accept="video/*" className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-medium file:bg-primary file:text-white hover:file:bg-blue-600 transition-colors" />
                  </div>
                </div>

                <div className="space-y-4">
                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">Video URL</label>
                    <input 
                      type="text" 
                      placeholder="https://..." 
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">Title</label>
                    <input 
                      type="text" 
                      placeholder="Video title" 
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">Description</label>
                    <textarea 
                      placeholder="Add a description..." 
                      rows={4}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary"
                    ></textarea>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-900 mb-2">Platforms</label>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <label className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                        <input type="checkbox" className="rounded text-primary focus:ring-primary" defaultChecked />
                        <span>TikTok</span>
                      </label>
                      <label className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                        <input type="checkbox" className="rounded text-primary focus:ring-primary" defaultChecked />
                        <span>YouTube Shorts</span>
                      </label>
                      <label className="flex items-center gap-2 p-3 border border-gray-300 rounded-lg cursor-pointer hover:bg-gray-50 transition-colors">
                        <input type="checkbox" className="rounded text-primary focus:ring-primary" defaultChecked />
                        <span>Instagram Reels</span>
                      </label>
                    </div>
                  </div>

                  <button className="w-full bg-primary text-white py-3 rounded-lg hover:bg-blue-600 transition-colors font-medium">
                    Upload and Process
                  </button>
                </div>
              </div>
            </div>
          )}

          {/* Analytics Section */}
          {activeTab === 'analytics' && (
            <div className="space-y-8">
              <h2 className="text-2xl font-bold text-gray-900">Analytics</h2>

              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Views vs Likes</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <BarChart data={analyticsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                        <YAxis stroke="#6b7280" fontSize={12} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                          }} 
                        />
                        <Bar dataKey="views" fill="#3b82f6" name="Views" />
                        <Bar dataKey="likes" fill="#10b981" name="Likes" />
                      </BarChart>
                    </ResponsiveContainer>
                  </div>
                </div>

                <div className="bg-white rounded-xl p-6 border border-gray-200">
                  <h3 className="text-lg font-semibold text-gray-900 mb-6">Engagement Rate</h3>
                  <div className="h-64">
                    <ResponsiveContainer width="100%" height="100%">
                      <LineChart data={analyticsData}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#f3f4f6" />
                        <XAxis dataKey="name" stroke="#6b7280" fontSize={12} />
                        <YAxis stroke="#6b7280" fontSize={12} />
                        <Tooltip 
                          contentStyle={{ 
                            backgroundColor: '#fff', 
                            border: '1px solid #e5e7eb', 
                            borderRadius: '8px',
                            boxShadow: '0 4px 6px -1px rgba(0, 0, 0, 0.1)'
                          }} 
                        />
                        <Line type="monotone" dataKey="comments" stroke="#8b5cf6" strokeWidth={2} dot={{ r: 3 }} />
                      </LineChart>
                    </ResponsiveContainer>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Accounts Section */}
          {activeTab === 'accounts' && (
            <div className="space-y-8">
              <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-gray-900">Connected Accounts</h2>
                <button className="bg-primary text-white px-4 py-2 rounded-lg hover:bg-blue-600 transition-colors flex items-center gap-2">
                  <Plus className="w-4 h-4" />
                  Add Account
                </button>
              </div>

              <div className="bg-white rounded-xl border border-gray-200 overflow-hidden">
                <div className="overflow-x-auto">
                  <table className="w-full">
                    <thead className="bg-gray-50">
                      <tr>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Platform</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Username</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Posts</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Views</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Engagement</th>
                        <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Actions</th>
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {accounts.map((account) => (
                        <tr key={account.id} className="hover:bg-gray-50 transition-colors">
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center">
                              <div className="w-8 h-8 bg-primary rounded-lg flex items-center justify-center text-white text-xs font-medium mr-3">
                                {account.platform.charAt(0)}
                              </div>
                              <div className="text-sm font-medium text-gray-900">{account.platform}</div>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="text-sm text-gray-900">{account.username}</div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full ${
                              account.status === 'Active' 
                                ? 'bg-green-100 text-green-800' 
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {account.status}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.posts}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.views.toLocaleString()}</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{account.engagement}%</td>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium">
                            <button className="text-primary hover:text-blue-600 mr-3">Settings</button>
                            <button className="text-gray-600 hover:text-gray-900">Disconnect</button>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default DashboardPage;
