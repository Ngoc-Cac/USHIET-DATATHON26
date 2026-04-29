import { useState, useMemo, useEffect } from 'react';
import { 
  BarChart, Bar, LineChart, Line, AreaChart, Area, XAxis, YAxis, 
  CartesianGrid, Tooltip, ResponsiveContainer, Cell, Legend,
  ScatterChart, Scatter, ZAxis, ComposedChart
} from 'recharts';
import { 
  LayoutDashboard, TrendingUp, Users, ShieldAlert, 
  ChevronRight, ArrowUpRight, ArrowDownRight, Info,
  Box, Map, Share2, Activity, Calendar, Filter, ChevronDown, Sun, Moon
} from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';
import { clsx, type ClassValue } from 'clsx';
import { twMerge } from 'tailwind-merge';

import { 
  generateYearlyData, REGION_DATA, CATEGORY_DATA, 
  SEGMENT_DATA, CHANNEL_DATA, PRODUCT_SCATTER, 
  OPS_DATA 
} from './mockData';

// --- Utility ---
function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

const formatCompact = (val: number) => 
  new Intl.NumberFormat('en-US', { notation: 'compact', maximumFractionDigits: 1 }).format(val);

// --- Global Components ---

const SlicerBar = () => (
  <div className="flex items-center gap-4 py-3 border-y border-slate-100/20 mb-6 px-1">
    <div className="flex items-center gap-2 text-slate-400 font-bold text-[10px] uppercase tracking-widest mr-2">
      <Filter size={12} /> filters
    </div>
    <div className="slicer-dropdown slicer-active">
      <span>Year: 2022</span>
      <ChevronDown size={12} />
    </div>
    <div className="slicer-dropdown">
      <span>Category: All</span>
      <ChevronDown size={12} />
    </div>
    <div className="slicer-dropdown">
      <span>Region: All</span>
      <ChevronDown size={12} />
    </div>
    <div className="slicer-dropdown">
      <span>Segment: All</span>
      <ChevronDown size={12} />
    </div>
    <div className="slicer-dropdown">
      <span>Channel: All</span>
      <ChevronDown size={12} />
    </div>
  </div>
);

const KPICard = ({ label, value, trend, prefix = "", suffix = "" }: any) => (
  <div className="dashboard-card group">
    <span className="kpi-label group-hover:text-brand-neon transition-colors">{label}</span>
    <div className="mt-1 flex items-baseline gap-1">
      <span className="text-slate-400 text-xs font-semibold">{prefix}</span>
      <span className="kpi-value">{value}</span>
      <span className="text-slate-400 text-xs font-semibold">{suffix}</span>
    </div>
    {trend !== undefined && (
      <div className={cn(
        "mt-1 text-[10px] font-bold flex items-center gap-0.5",
        trend > 0 ? "text-status-success" : "text-status-error"
      )}>
        {trend > 0 ? <ArrowUpRight size={10} /> : <ArrowDownRight size={10} />}
        {Math.abs(trend)}% vs LW
      </div>
    )}
  </div>
);

const SectionTitle = ({ title, subtitle }: any) => (
  <div className="mb-4">
    <h3 className="text-xs font-black uppercase tracking-widest leading-none border-l-3 border-brand-neon pl-2">{title}</h3>
    {subtitle && <p className="text-[9px] text-slate-400 mt-1 font-bold italic">{subtitle}</p>}
  </div>
);

// --- Pages ---

const ExecutiveOverview = ({ data, theme }: { data: any[], theme: string }) => {
  const latest = data[data.length - 1];
  const prev = data[data.length - 2];
  const getTrend = (cur: number, p: number) => Math.round(((cur - p) / p) * 100);
  const chartTextColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  const gridColor = theme === 'dark' ? '#ffffff10' : '#00000008';

  return (
    <div className="grid grid-cols-12 gap-5 h-full">
      <div className="col-span-12">
        <SlicerBar />
      </div>

      <div className="col-span-12 grid grid-cols-2 md:grid-cols-4 lg:grid-cols-8 gap-3">
        <KPICard label="Revenue" value={formatCompact(latest.revenue)} prefix="$" trend={getTrend(latest.revenue, prev.revenue)} />
        <KPICard label="Net Profit" value={formatCompact(latest.profit)} prefix="$" trend={getTrend(latest.profit, prev.profit)} />
        <KPICard label="Margin %" value={latest.margin.toFixed(1)} suffix="%" trend={getTrend(latest.margin, prev.margin)} />
        <KPICard label="Orders" value={formatCompact(latest.orders)} trend={getTrend(latest.orders, prev.orders)} />
        <KPICard label="AOV" value={latest.aov.toFixed(1)} prefix="$" trend={2.4} />
        <KPICard label="Customers" value={formatCompact(latest.customers)} trend={getTrend(latest.customers, prev.customers)} />
        <KPICard label="Returns" value={latest.returnRate.toFixed(1)} suffix="%" trend={-1.2} />
        <KPICard label="Rating" value={latest.rating.toFixed(1)} suffix="/5" trend={0.5} />
      </div>

      <div className="col-span-12 lg:col-span-8 dashboard-card">
        <SectionTitle title="Revenue & Profit Trend" subtitle="Net performance trajectory [2012-2022]" />
        <ResponsiveContainer width="100%" height={240}>
          <AreaChart data={data}>
            <defs>
              <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#90FF00" stopOpacity={0.2}/>
                <stop offset="95%" stopColor="#90FF00" stopOpacity={0}/>
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={gridColor} />
            <XAxis dataKey="year" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor}} />
            <YAxis axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor}} tickFormatter={formatCompact} />
            <Tooltip contentStyle={{ borderRadius: '8px', border: `1px solid ${theme === 'dark' ? '#90FF0033' : '#e2e8f0'}`, background: theme === 'dark' ? '#0A0A0A' : '#fff', fontSize: '11px' }} />
            <Legend verticalAlign="top" height={36} iconType="circle" />
            <Area type="monotone" dataKey="revenue" name="Revenue" stroke="#90FF00" fillOpacity={1} fill="url(#colorRev)" strokeWidth={3} />
            <Area type="monotone" dataKey="profit" stroke={theme === 'dark' ? '#fff' : '#0B1F3B'} fillOpacity={0} strokeWidth={2} strokeDasharray="5 5" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-4 dashboard-card">
        <SectionTitle title="Revenue by Region" subtitle="Geographic contribution ranking" />
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={REGION_DATA} layout="vertical">
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor, fontWeight: 'bold'}} width={80} />
            <Bar dataKey="revenue" fill="#90FF00" radius={[0, 4, 4, 0]} barSize={20}>
              {REGION_DATA.map((entry, index) => (
                <Cell key={`cell-${index}`} fillOpacity={1 - (index * 0.15)} fill="#90FF00" />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-9 dashboard-card">
        <SectionTitle title="Category Performance" subtitle="Volume vs Profitability index per business unit" />
        <ResponsiveContainer width="100%" height={240}>
          <ComposedChart data={CATEGORY_DATA}>
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor}} />
            <YAxis yAxisId="left" orientation="left" axisLine={false} tickLine={false} tickFormatter={formatCompact} tick={{fontSize: 10, fill: chartTextColor}} />
            <YAxis yAxisId="right" orientation="right" axisLine={false} tickLine={false} tickFormatter={(v) => `${v}%`} tick={{fontSize: 10, fill: chartTextColor}} />
            <Tooltip contentStyle={{ background: theme === 'dark' ? '#0A0A0A' : '#fff', border: 'none' }} />
            <Bar yAxisId="left" dataKey="revenue" fill={theme === 'dark' ? "#90FF0020" : "#f1f5f9"} stroke="#90FF00" radius={[4, 4, 0, 0]} barSize={40} name="Revenue ($)" />
            <Line yAxisId="right" dataKey="margin" stroke="#90FF00" strokeWidth={3} dot={{r: 4, fill: '#90FF00'}} name="Margin (%)" />
          </ComposedChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-3 flex flex-col gap-4">
        <div className="insight-box h-full">
          <SectionTitle title="Executive Insights" subtitle="Diagnostic summary" />
          <ul className="text-[10px] space-y-3 list-none font-bold uppercase tracking-tight">
            <li className="flex gap-2">
              <span className="text-brand-neon">/01</span>
              <span><strong>Growth:</strong> Revenue surged 32% in 2022 following digital channel pivot.</span>
            </li>
            <li className="flex gap-2">
              <span className="text-brand-neon">/02</span>
              <span><strong>Margin:</strong> Accessories category maintains highest efficiency (18.4%).</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

const SalesProfitability = ({ theme }: any) => {
  const chartTextColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  return (
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-12">
        <SlicerBar />
      </div>

      <div className="col-span-12 dashboard-card h-[400px]">
        <SectionTitle title="Revenue vs Margin Scatter" subtitle="Diagnostic analysis per product SKU [Size = Units Sold]" />
        <ResponsiveContainer width="100%" height={320}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme === 'dark' ? '#ffffff10' : '#00000008'} />
            <XAxis type="number" dataKey="revenue" name="Revenue" unit="$" axisLine={false} tickFormatter={formatCompact} tick={{fill: chartTextColor}} />
            <YAxis type="number" dataKey="margin" name="Margin" unit="%" axisLine={false} tick={{fill: chartTextColor}} />
            <ZAxis type="number" dataKey="units" range={[60, 400]} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Products" data={PRODUCT_SCATTER}>
              {PRODUCT_SCATTER.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.margin > 30 ? '#90FF00' : entry.margin < 15 ? '#FF3B3B' : '#6366F1'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card">
        <SectionTitle title="Revenue & Profit by Category" />
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={CATEGORY_DATA} layout="vertical">
            <XAxis type="number" hide />
            <YAxis dataKey="name" type="category" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor}} width={80} />
            <Bar dataKey="revenue" fill="#90FF00" radius={[0, 4, 4, 0]} barSize={10} name="Revenue" />
            <Bar dataKey="profit" fill={theme === 'dark' ? '#fff' : '#0B1F3B'} radius={[0, 4, 4, 0]} barSize={10} name="Profit" />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card">
        <SectionTitle title="Revenue & Margin by Segment" />
        <ResponsiveContainer width="100%" height={240}>
          <ComposedChart data={SEGMENT_DATA}>
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fontSize: 10, fill: chartTextColor}} />
            <YAxis yAxisId="left" orientation="left" axisLine={false} tick={{fill: chartTextColor}} />
            <YAxis yAxisId="right" orientation="right" axisLine={false} tick={{fill: chartTextColor}} />
            <Bar yAxisId="left" dataKey="revenue" fill="#90FF00" radius={[4, 4, 0, 0]} barSize={40} />
            <Line yAxisId="right" dataKey="margin" stroke="#FFB800" strokeWidth={3} dot={{r: 5, fill: '#FFB800'}} />
          </ComposedChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const CustomerChannel = ({ theme }: any) => {
  const data = useMemo(() => generateYearlyData(), []);
  const chartTextColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  return (
    <div className="grid grid-cols-12 gap-5">
      <div className="col-span-12">
        <SlicerBar />
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card h-[300px]">
        <SectionTitle title="Orders per Customer by Age Group" />
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={[{name: '18-24', val: 2.1}, {name: '25-34', val: 3.4}, {name: '35-44', val: 2.8}, {name: '45+', val: 1.9}]}>
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <YAxis axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <Bar dataKey="val" fill="#90FF00" radius={[4, 4, 0, 0]} barSize={40} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card h-[300px]">
        <SectionTitle title="Revenue by Acquisition Channel" />
        <ResponsiveContainer width="100%" height={220}>
          <BarChart data={CHANNEL_DATA}>
            <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <YAxis axisLine={false} tickLine={false} hide />
            <Bar dataKey="revenue" fill="#90FF00" radius={[4, 4, 0, 0]} barSize={20} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-8 dashboard-card overflow-x-auto">
        <SectionTitle title="Region × Channel Satisfaction Matrix" />
        <table className="w-full text-xs mt-4">
          <thead className={cn("uppercase font-black text-[9px] tracking-widest", theme === 'dark' ? 'bg-white/5 text-slate-500' : 'bg-slate-50 text-slate-500')}>
            <tr>
              <th className="px-4 py-3 text-left">Region</th>
              <th className="px-4 py-3 text-right">Direct</th>
              <th className="px-4 py-3 text-right">Social</th>
              <th className="px-4 py-3 text-right">Search</th>
              <th className="px-4 py-3 text-right">Email</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-slate-100/5">
            {['North', 'South', 'Central'].map(r => (
              <tr key={r} className="hover:bg-brand-neon/5 transition-colors">
                <td className={cn("px-4 py-4 font-bold", theme === 'dark' ? 'text-white' : 'text-slate-900')}>{r}</td>
                <td className="px-4 py-4 text-right">4.2 <span className="text-[10px] text-slate-400">/5</span></td>
                <td className="px-4 py-4 text-right">3.8 <span className="text-[10px] text-slate-400">/5</span></td>
                <td className="px-4 py-4 text-right font-bold text-brand-neon">4.5 <span className="text-[10px] text-slate-400">/5</span></td>
                <td className="px-4 py-4 text-right">4.1 <span className="text-[10px] text-slate-400">/5</span></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div className="col-span-12 lg:col-span-4 dashboard-card">
        <SectionTitle title="New vs Repeat Customers" />
        <ResponsiveContainer width="100%" height={200}>
          <AreaChart data={data}>
            <XAxis dataKey="year" axisLine={false} hide />
            <YAxis hide />
            <Tooltip />
            <Area type="monotone" dataKey="repeatCustomers" stackId="1" stroke={theme === 'dark' ? '#fff' : '#0B1F3B'} fill={theme === 'dark' ? '#fff' : '#0B1F3B'} fillOpacity={0.4} />
            <Area type="monotone" dataKey="newCustomers" stackId="1" stroke="#90FF00" fill="#90FF00" fillOpacity={0.6} />
          </AreaChart>
        </ResponsiveContainer>
      </div>
    </div>
  );
};

const OperationsRisk = ({ theme }: any) => {
  const chartTextColor = theme === 'dark' ? '#94a3b8' : '#64748b';
  return (
    <div className="grid grid-cols-12 gap-5 h-full">
      <div className="col-span-12">
        <SlicerBar />
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card">
        <SectionTitle title="Return Rate by Size Category" />
        <ResponsiveContainer width="100%" height={240}>
          <BarChart data={OPS_DATA.returnsBySize}>
            <XAxis dataKey="size" axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <YAxis axisLine={false} tickLine={false} unit="%" tick={{fill: chartTextColor}} />
            <Bar dataKey="rate" fill="#FF3B3B" radius={[4, 4, 0, 0]} barSize={30} />
          </BarChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-6 dashboard-card">
        <SectionTitle title="Delivery Speed vs UX Rating" />
        <ResponsiveContainer width="100%" height={240}>
          <LineChart data={OPS_DATA.deliveryVsRating}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme === 'dark' ? '#ffffff10' : '#f1f5f9'} />
            <XAxis dataKey="days" axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <YAxis domain={[0, 5]} axisLine={false} tickLine={false} tick={{fill: chartTextColor}} />
            <Line type="monotone" dataKey="rating" stroke="#90FF00" strokeWidth={4} dot={{r: 6, fill: theme === 'dark' ? '#050505' : '#0B1F3B', strokeWidth: 2, stroke: '#90FF00'}} />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-8 dashboard-card h-[350px]">
        <SectionTitle title="Stockout Rate vs Revenue Impact" />
        <ResponsiveContainer width="100%" height={280}>
          <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 20 }}>
            <CartesianGrid strokeDasharray="3 3" vertical={false} stroke={theme === 'dark' ? '#ffffff10' : '#f1f5f9'} />
            <XAxis type="number" dataKey="stockout" name="Stockout Rate" unit="%" tick={{fill: chartTextColor}} />
            <YAxis type="number" dataKey="revenue" name="Rev Impact" unit="$" tickFormatter={formatCompact} tick={{fill: chartTextColor}} />
            <Tooltip cursor={{ strokeDasharray: '3 3' }} />
            <Scatter name="Risk" data={[{stockout: 12, revenue: 45000}, {stockout: 5, revenue: 12000}, {stockout: 18, revenue: 89000}]}>
              {[{stockout: 12, revenue: 45000}, {stockout: 5, revenue: 12000}, {stockout: 18, revenue: 89000}].map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.stockout > 10 ? '#FF3B3B' : '#FFB800'} />
              ))}
            </Scatter>
          </ScatterChart>
        </ResponsiveContainer>
      </div>

      <div className="col-span-12 lg:col-span-4 dashboard-card border-l-2 border-status-error">
        <SectionTitle title="Prescriptive Actions" />
        <div className="mt-4 space-y-4">
           <div className="insight-box">
             <p className={cn("text-[10px] font-black uppercase", theme === 'dark' ? 'text-brand-neon' : 'text-slate-900')}>Logistics Threshold</p>
             <p className="text-[11px] text-slate-500 mt-1 font-bold italic leading-tight">Delivery exceeding 4 days correlates with &gt;1.5pt satisfaction drop. Recommendation: Localize distribution.</p>
           </div>
           <div className="insight-box">
             <p className={cn("text-[10px] font-black uppercase", theme === 'dark' ? 'text-brand-neon' : 'text-slate-900')}>Sizing Standards</p>
             <p className="text-[11px] text-slate-500 mt-1 font-bold italic leading-tight">XXL category shows 22% return rate. Recommendation: Immediate review of pattern-block consistency.</p>
           </div>
        </div>
      </div>
    </div>
  );
};

// --- Main App ---

export default function App() {
  const [currentPage, setCurrentPage] = useState('executive');
  const [theme, setTheme] = useState<'light' | 'dark'>('dark');
  const [loading, setLoading] = useState(false);
  const yearlyData = useMemo(() => generateYearlyData(), []);

  useEffect(() => {
    document.body.className = theme === 'dark' ? 'dark-theme' : '';
  }, [theme]);

  const changePage = (page: string) => {
    setLoading(true);
    setTimeout(() => {
      setCurrentPage(page);
      setLoading(false);
    }, 300);
  };

  const toggleTheme = () => setTheme(theme === 'dark' ? 'light' : 'dark');

  return (
    <div className={cn(
      "min-h-screen flex selection:bg-brand-neon selection:text-black overflow-hidden",
      theme === 'dark' ? "bg-[#050505]" : "bg-white"
    )}>
      {/* Fixed Sidebar */}
      <aside className={cn(
        "w-16 lg:w-56 flex flex-col h-full fixed z-40 transition-all duration-300",
        theme === 'dark' ? "bg-black border-r border-white/10" : "bg-white border-r border-slate-100"
      )}>
        <div className="p-6 shrink-0">
          <div className="flex items-center gap-2 text-brand-neon font-black text-xs tracking-widest uppercase">
            <div className="w-8 h-8 bg-brand-neon rounded grid place-items-center shrink-0">
              <Box size={18} className="text-black" />
            </div>
            <span className={cn("hidden lg:inline", theme === 'dark' ? "text-white" : "text-black")}>Gridbreaker</span>
          </div>
          <div className="hidden lg:block text-[8px] font-bold text-brand-neon mt-1 uppercase tracking-[0.3em]">Datathon [2026]</div>
        </div>

        <nav className="flex-1 mt-6">
          <button onClick={() => changePage('executive')} className={cn("sidebar-link", currentPage === 'executive' && "sidebar-link-active")}>
             <LayoutDashboard size={18} />
             <span className="hidden lg:inline">Overview</span>
          </button>
          <button onClick={() => changePage('sales')} className={cn("sidebar-link", currentPage === 'sales' && "sidebar-link-active")}>
             <TrendingUp size={18} />
             <span className="hidden lg:inline">Profitability</span>
          </button>
          <button onClick={() => changePage('customer')} className={cn("sidebar-link", currentPage === 'customer' && "sidebar-link-active")}>
             <Users size={18} />
             <span className="hidden lg:inline">Customers</span>
          </button>
          <button onClick={() => changePage('ops')} className={cn("sidebar-link", currentPage === 'ops' && "sidebar-link-active")}>
             <ShieldAlert size={18} />
             <span className="hidden lg:inline">Risk Vectors</span>
          </button>
        </nav>

        <div className="p-4 mt-auto">
          <button 
             onClick={toggleTheme}
             className={cn(
               "w-full flex items-center justify-center gap-2 py-2 rounded-lg border transition-all duration-300",
               theme === 'dark' ? "bg-white/5 border-white/10 text-white hover:bg-white/10" : "bg-slate-50 border-slate-200 text-slate-600 hover:bg-slate-100"
             )}
          >
             {theme === 'dark' ? <Sun size={14} /> : <Moon size={14} />}
             <span className="hidden lg:inline text-[9px] font-black uppercase tracking-widest">{theme === 'dark' ? 'Light' : 'Dark'} Mode</span>
          </button>
          
          <div className="hidden lg:block mt-4 p-3 rounded bg-brand-neon/5 border border-brand-neon/10">
             <p className="text-[9px] text-slate-500 font-bold uppercase tracking-widest">VinTelligence</p>
             <p className="text-[8px] text-brand-neon font-black mt-1 uppercase">BTC Core Team</p>
          </div>
        </div>
      </aside>

      {/* Content Stage */}
      <main className="flex-1 ml-16 lg:ml-56 h-screen overflow-hidden p-6 lg:px-10 lg:py-8 relative flex flex-col">
        <header className="mb-4 shrink-0 flex justify-between items-end">
          <div>
            <div className="flex items-center gap-2 text-brand-neon font-black text-[8px] uppercase tracking-[0.3em] mb-1 leading-none">
              <span>CANVAS_STAGE</span>
              <ChevronRight size={8} />
              <span className="text-slate-500">OPTIMIZED_16:9</span>
            </div>
            <h1 className={cn("text-3xl font-black tracking-tighter uppercase italic leading-none", theme === 'dark' ? "text-white" : "text-black")}>
              {currentPage === 'executive' && "Executive Overview"}
              {currentPage === 'sales' && "Sales & Profitability"}
              {currentPage === 'customer' && "Customer & Channel"}
              {currentPage === 'ops' && "Operations & Risk Control"}
            </h1>
          </div>
          <div className="hidden lg:block text-[9px] font-black text-brand-neon/40 uppercase tracking-[0.4em]">
             GRIDBREAKER_ANALYTICS: ACTIVE
          </div>
        </header>

        <div className="flex-1 min-h-0 flex flex-col overflow-hidden">
          <AnimatePresence mode="wait">
            {loading ? (
              <motion.div 
                key="loader"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className={cn("absolute inset-0 z-50 flex items-center justify-center backdrop-blur-sm", theme === 'dark' ? "bg-black/40" : "bg-white/40")}
              >
                <div className="w-10 h-10 border-4 border-slate-800 border-t-brand-neon rounded-full animate-spin"></div>
              </motion.div>
            ) : (
              <motion.div
                key={currentPage}
                initial={{ opacity: 0, scale: 0.99, filter: 'blur(10px)' }}
                animate={{ opacity: 1, scale: 1, filter: 'blur(0px)' }}
                exit={{ opacity: 0, scale: 0.99, filter: 'blur(10px)' }}
                transition={{ duration: 0.3, ease: 'easeOut' }}
                className="h-full flex flex-col"
              >
                {currentPage === 'executive' && <ExecutiveOverview theme={theme} data={yearlyData} />}
                {currentPage === 'sales' && <SalesProfitability theme={theme} />}
                {currentPage === 'customer' && <CustomerChannel theme={theme} />}
                {currentPage === 'ops' && <OperationsRisk theme={theme} />}
              </motion.div>
            )}
          </AnimatePresence>
        </div>

        <footer className="mt-4 pt-4 border-t border-slate-500/10 flex justify-between text-[8px] font-black text-slate-500 uppercase tracking-widest shrink-0">
           <p>© 2026 Gridbreaker // 16:9 [FIXED_VIEWPORT]</p>
           <div className="flex gap-6">
              <span className="text-[7px]">SYSTEM: {theme.toUpperCase()}_ENGINE</span>
              <span className="text-brand-neon font-mono">BTC: CORE_BUILT</span>
           </div>
        </footer>
      </main>
    </div>
  );
}





