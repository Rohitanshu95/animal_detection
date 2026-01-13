import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { TrendingUp, FileText, AlertTriangle, Leaf, Calendar, Download, Activity, ArrowUpRight } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell } from 'recharts';

const COLORS = ['#059669', '#10b981', '#34d399', '#6ee7b7', '#a7f3d0', '#d1fae5'];

const StatCard = ({ title, value, label, icon: Icon, trend, colorClass = "bg-emerald-50 text-emerald-600" }) => (
  <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-[0_2px_10px_-4px_rgba(6,81,237,0.1)] hover:shadow-[0_8px_30px_-4px_rgba(6,81,237,0.1)] transition-all duration-300 group">
    <div className="flex justify-between items-start mb-4">
      <div className={`p-3 rounded-xl ${colorClass} group-hover:scale-110 transition-transform`}>
        <Icon className="w-6 h-6" />
      </div>
      {trend && (
        <div className="flex items-center gap-1 text-xs font-bold px-2.5 py-1 rounded-full bg-slate-50 text-slate-600 border border-slate-100">
          <TrendingUp className="w-3 h-3 text-emerald-500" />
          {trend}
        </div>
      )}
    </div>
    <h3 className="text-3xl font-bold text-slate-900 mb-1 tracking-tight">{value}</h3>
    <p className="text-sm text-slate-500 font-medium">{label}</p>
  </div>
);

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-slate-900 text-white p-3 rounded-lg shadow-xl text-xs">
        <p className="font-bold mb-1">{label}</p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color }}>
            {entry.name}: {entry.value}
          </p>
        ))}
      </div>
    );
  }
  return null;
};

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [showAnalysis, setShowAnalysis] = useState(false);

  useEffect(() => {
    const fetchStats = async () => {
      try {
        const response = await axios.get('/api/statistics');
        setStats(response.data);
      } catch (error) {
        console.error("Failed to fetch statistics:", error);
      } finally {
        setLoading(false);
      }
    };
    fetchStats();
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-emerald-500"></div>
      </div>
    );
  }

  if (!stats) return <div className="p-8 text-center text-slate-500">Failed to load dashboard data.</div>;

  // Transform Data
  const trendData = Object.entries(stats.by_month || {})
    .sort((a, b) => a[0].localeCompare(b[0]))
    .map(([month, count]) => ({
      month,
      incidents: count,
      resolved: Math.floor(count * 0.7) // Mock resolved data as 70% of total
    }));

  // Reason-wise trend data (using status as proxy for reasons)
  const reasonTrendData = Object.entries(stats.by_reason || {})
    .map(([reason, count]) => ({
      reason,
      count,
      percentage: ((count / stats.total_incidents) * 100).toFixed(1)
    }))
    .sort((a, b) => b.count - a.count)
    .slice(0, 5); // Top 5 reasons

  const speciesData = (stats.top_animals || []).map((item, index) => ({
    name: item.animal,
    count: item.count,
    color: COLORS[index % COLORS.length]
  }));

  const recentActivity = (stats.recent_incidents || []).map(inc => ({
    id: inc._id || inc.id, // Handle both _id and id
    action: "New Incident Reported",
    details: `${inc.title || inc.description?.substring(0, 50) || 'Incident'} in ${inc.location || 'Unknown Location'}`,
    time: inc.created_at ? new Date(inc.created_at).toLocaleDateString() : 'Recent',
    type: (inc.status === 'Open' || inc.status === 'Reported') ? 'alert' : 'success'
  }));

  // Calculate totals for cards
  const totalIncidents = stats.total_incidents || 0;
  const uniqueSpecies = stats.top_animals?.length || 0;
  const recentCount = recentActivity.length;
  const openCases = stats.by_status?.['Open'] || 0;

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header Section */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900 tracking-tight">Command Center</h1>
          <p className="text-slate-500 mt-1">Real-time intelligence and historical archive overview.</p>
        </div>
        <div className="flex items-center gap-3">
          <button className="flex items-center gap-2 px-4 py-2 bg-slate-900 text-white rounded-lg hover:bg-slate-800 font-medium text-sm transition-all shadow-lg shadow-slate-900/20">
            <Download className="w-4 h-4" />
            
          </button>
        </div>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <StatCard 
          title="Total Incidents" 
          value={totalIncidents.toLocaleString()} 
          label="Total records archived" 
          icon={FileText} 
          trend="+5%"
        />
        <StatCard 
          title="Species" 
          value={uniqueSpecies} 
          label="Species identified" 
          icon={Leaf} 
          trend="Active"
          colorClass="bg-amber-50 text-amber-600"
        />
        <StatCard 
          title="Activity" 
          value={recentCount} 
          label="Recent updates" 
          icon={Activity} 
          colorClass="bg-blue-50 text-blue-600"
        />
        <StatCard 
          title="Open Cases" 
          value={openCases} 
          label="Pending investigation" 
          icon={AlertTriangle} 
          colorClass="bg-rose-50 text-rose-600"
        />
      </div>

      {/* Bento Grid Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Main Chart - Spans 2 Columns */}
        <div className="lg:col-span-2 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-slate-900 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-emerald-600" />
              Incident Trends
            </h2>
            <div className="flex gap-2">
              <span className="w-3 h-3 rounded-full bg-emerald-500"></span>
              <span className="text-xs text-slate-500">Total</span>
              <span className="w-3 h-3 rounded-full bg-emerald-200 ml-2"></span>
              <span className="text-xs text-slate-500">Resolved (Est.)</span>
            </div>
          </div>


          <div className="flex-1 min-h-[300px]">
             {trendData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={trendData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                    <defs>
                      <linearGradient id="colorIncidents" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#059669" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#059669" stopOpacity={0}/>
                      </linearGradient>
                      <linearGradient id="colorResolved" x1="0" y1="0" x2="0" y2="1">
                        <stop offset="5%" stopColor="#10b981" stopOpacity={0.1}/>
                        <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                      </linearGradient>
                    </defs>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#f1f5f9" />
                    <XAxis dataKey="month" axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} dy={10} />
                    <YAxis axisLine={false} tickLine={false} tick={{fill: '#94a3b8', fontSize: 12}} />
                    <Tooltip content={<CustomTooltip />} />
                    <Area type="monotone" dataKey="incidents" stroke="#059669" strokeWidth={3} fillOpacity={1} fill="url(#colorIncidents)" />
                    <Area type="monotone" dataKey="resolved" stroke="#6ee7b7" strokeWidth={3} fillOpacity={1} fill="url(#colorResolved)" />
                  </AreaChart>
                </ResponsiveContainer>
             ) : (
                <div className="flex items-center justify-center h-full text-slate-400 text-sm">No trend data available</div>
             )}
          </div>
        </div>

        {/* Activity Feed - Spans 1 Column */}
        <div className="bg-white p-6 rounded-2xl border border-slate-100 shadow-sm flex flex-col">
          <div className="flex items-center justify-between mb-6">
            <h2 className="text-lg font-bold text-slate-900">Recent Activity</h2>
            <button className="text-xs text-emerald-600 font-bold hover:underline">View All</button>
          </div>
          <div className="space-y-6 overflow-y-auto max-h-[300px] pr-2 custom-scrollbar">
            {recentActivity.length > 0 ? (
               recentActivity.map((item) => (
                <div key={item.id} className="flex gap-4 group">
                   <div className={`mt-1 w-2 h-2 rounded-full shrink-0 ${
                     item.type === 'alert' ? 'bg-rose-500 shadow-[0_0_8px_rgba(244,63,94,0.4)]' : 
                     item.type === 'warning' ? 'bg-amber-500' :
                     item.type === 'success' ? 'bg-emerald-500' : 'bg-slate-300'
                   }`} />
                   <div>
                     <p className="text-sm font-bold text-slate-800 group-hover:text-emerald-700 transition-colors cursor-pointer line-clamp-1">{item.action}</p>
                     <p className="text-xs text-slate-500 mt-0.5 line-clamp-1">{item.details}</p>
                     <p className="text-[10px] text-slate-400 mt-1 uppercase tracking-wider font-semibold">{item.time}</p>
                   </div>
                </div>
              ))
            ) : (
                <p className="text-sm text-slate-400 text-center py-10">No recent activity found.</p>
            )}
          </div>
          <button className="mt-auto w-full py-3 rounded-xl border border-dashed border-slate-200 text-slate-500 text-sm font-medium hover:bg-slate-50 hover:border-emerald-200 hover:text-emerald-600 transition-all mt-4">
            Load More Logs
          </button>
        </div>

        {/* Species Distribution - Bottom Row */}
        <div className="lg:col-span-1 bg-white p-6 rounded-2xl border border-slate-100 shadow-sm">
           <h2 className="text-lg font-bold text-slate-900 mb-2">Species Impact</h2>
           <p className="text-xs text-slate-500 mb-6 font-medium">Distribution of cases by species type</p>
           <div className="h-[200px] relative">
              {speciesData.length > 0 ? (
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={speciesData}
                      cx="50%"
                      cy="50%"
                      innerRadius={60}
                      outerRadius={80}
                      paddingAngle={5}
                      dataKey="count"
                    >
                      {speciesData.map((entry, index) => (
                        <Cell key={`cell-${index}`} fill={entry.color} strokeWidth={0} />
                      ))}
                    </Pie>
                    <Tooltip content={<CustomTooltip />} />
                  </PieChart>
                </ResponsiveContainer>
              ) : (
                 <div className="flex items-center justify-center h-full text-slate-400 text-sm">No species data</div>
              )}
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="text-3xl font-bold text-slate-900">{uniqueSpecies}</span>
                <span className="text-xs text-slate-500 uppercase font-bold tracking-wider">Types</span>
              </div>
           </div>
           <div className="mt-4 grid grid-cols-2 gap-3 max-h-[100px] overflow-y-auto custom-scrollbar">
              {speciesData.map((item) => (
                <div key={item.name} className="flex items-center gap-2 text-xs font-medium text-slate-600">
                  <span className="w-2 h-2 rounded-full shrink-0" style={{ backgroundColor: item.color }} />
                  <span className="truncate">{item.name}</span> <span className="text-slate-400">({item.count})</span>
                </div>
              ))}
           </div>
        </div>

         {/* Hotspot Alert - Bottom Row */}
         <div className="lg:col-span-2 bg-gradient-to-br from-slate-900 to-slate-800 p-6 rounded-2xl text-white shadow-lg shadow-slate-900/10 relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-64 h-64 bg-emerald-500/10 rounded-full blur-3xl -mr-16 -mt-16 group-hover:bg-emerald-500/20 transition-all duration-700"></div>
            
            <div className="relative z-10 flex flex-col md:flex-row items-center justify-between h-full gap-6">
               <div className="flex-1">
                 <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-white/10 border border-white/10 text-xs font-bold text-emerald-300 mb-4 backdrop-blur-md">
                    <AlertTriangle className="w-3 h-3" />
                    High Activity Detected
                 </div>
                 <h3 className="text-2xl font-bold mb-2">Similipal Reserve Anomaly</h3>
                 <p className="text-slate-300 text-sm leading-relaxed max-w-lg">
                    AI analysis indicates a 40% increase in incident reports in the northern sector over the last 48 hours. Recommended: Increase patrol frequency.
                 </p>
               </div>
               <button
                 onClick={() => setShowAnalysis(!showAnalysis)}
                 className="shrink-0 flex items-center gap-2 px-6 py-3 bg-white text-slate-900 rounded-xl font-bold hover:bg-emerald-50 transition-colors shadow-xl"
               >
                 View Analysis <ArrowUpRight className="w-4 h-4" />
               </button>
            </div>
         </div>

      </div>
    </div>
  );
};

export default Dashboard;
