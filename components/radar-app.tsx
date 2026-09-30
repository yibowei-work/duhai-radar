'use client';

import { useMemo, useRef, useState } from 'react';
import {
  ArrowRight,
  ArrowUpRight,
  Banknote,
  Box,
  Building2,
  CalendarClock,
  CheckCircle2,
  ChevronRight,
  CircleAlert,
  CircleDollarSign,
  Compass,
  FileCheck2,
  Filter,
  Lightbulb,
  Megaphone,
  PackageCheck,
  Radar,
  RefreshCw,
  Search,
  ShieldAlert,
  ShoppingBag,
  Sparkles,
  Store,
  Target,
  TrendingUp,
  X,
} from 'lucide-react';

import rawData from '@/data/intel.json';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import {
  Card,
  CardAction,
  CardContent,
  CardHeader,
  CardTitle,
} from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import {
  NativeSelect,
  NativeSelectOption,
} from '@/components/ui/native-select';

type Impact = 'opportunity' | 'risk' | 'mixed';

type IntelligenceItem = {
  id: string;
  title: string;
  summary: string;
  pm_takeaway: string;
  action: string;
  published_at: string;
  brand: string;
  market: string;
  category: string;
  signal_type: string;
  impact: Impact;
  stage: string;
  score: number;
  confidence: number;
  source: string;
  source_tier: string;
  source_url: string;
  tags: string[];
};

type IntelligenceData = {
  version: number;
  meta: {
    generated_at: string;
    window_start: string;
    window_end: string;
    review_mode: string;
    next_run_at: string;
    source_health: {
      healthy: number;
      delayed: number;
      total: number;
    };
  };
  items: IntelligenceItem[];
};

const data = rawData as IntelligenceData;

const categoryOptions = [
  { key: 'all', label: '全部信号', icon: Radar },
  { key: '品牌与扩张', label: '品牌与扩张', icon: Building2 },
  { key: '产品与包装', label: '产品与包装', icon: Box },
  { key: '营销与内容', label: '营销与内容', icon: Megaphone },
  { key: '渠道与电商', label: '渠道与电商', icon: Store },
  { key: '物流与履约', label: '物流与履约', icon: PackageCheck },
  { key: '支付与金融', label: '支付与金融', icon: Banknote },
  { key: '政策与合规', label: '政策与合规', icon: FileCheck2 },
  { key: '市场与消费', label: '市场与消费', icon: TrendingUp },
];

const impactCopy: Record<Impact, { label: string; className: string; icon: typeof Sparkles }> = {
  opportunity: {
    label: '机会',
    className: 'bg-emerald-100 text-emerald-800 dark:bg-emerald-950 dark:text-emerald-200',
    icon: Sparkles,
  },
  risk: {
    label: '风险',
    className: 'bg-rose-100 text-rose-800 dark:bg-rose-950 dark:text-rose-200',
    icon: ShieldAlert,
  },
  mixed: {
    label: '混合信号',
    className: 'bg-amber-100 text-amber-800 dark:bg-amber-950 dark:text-amber-200',
    icon: CircleAlert,
  },
};

const reviewModeCopy: Record<string, string> = {
  daily_3d: '近 3 日日常核查',
  weekly_month_to_date: '本月完整回查',
  monthly_previous_month: '上月完整回查',
  catch_up: '漏跑补查',
};

const pmLensByCategory: Record<string, typeof Lightbulb> = {
  品牌与扩张: Compass,
  产品与包装: Box,
  营销与内容: Megaphone,
  渠道与电商: ShoppingBag,
  物流与履约: PackageCheck,
  支付与金融: CircleDollarSign,
  政策与合规: ShieldAlert,
  市场与消费: TrendingUp,
};

function formatDate(value: string, withYear = false) {
  return new Intl.DateTimeFormat('zh-CN', {
    ...(withYear ? { year: 'numeric' as const } : {}),
    month: 'short',
    day: 'numeric',
    timeZone: 'Asia/Shanghai',
  }).format(new Date(value));
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat('zh-CN', {
    month: 'numeric',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
    hour12: false,
    timeZone: 'Asia/Shanghai',
  }).format(new Date(value));
}

function scoreTone(score: number) {
  if (score >= 9) return 'text-primary';
  if (score >= 8.5) return 'text-amber-700 dark:text-amber-300';
  return 'text-foreground';
}

function matchesPeriod(item: IntelligenceItem, period: string) {
  if (period === 'all') return true;
  const itemDate = new Date(item.published_at);
  const anchor = new Date(`${data.meta.window_end}T23:59:59+08:00`);
  if (period === '3d') {
    const start = new Date(anchor);
    start.setDate(start.getDate() - 2);
    start.setHours(0, 0, 0, 0);
    return itemDate >= start && itemDate <= anchor;
  }
  if (period === 'month') {
    return (
      itemDate.getFullYear() === anchor.getFullYear() &&
      itemDate.getMonth() === anchor.getMonth()
    );
  }
  return true;
}

function SignalCard({ item, featured = false }: { item: IntelligenceItem; featured?: boolean }) {
  const impact = impactCopy[item.impact];
  const ImpactIcon = impact.icon;
  const LensIcon = pmLensByCategory[item.category] ?? Lightbulb;

  if (featured) {
    return (
      <Card className="signal-card group gap-0 rounded-[22px] border-0 py-0 ring-1 ring-border transition-all duration-300 hover:-translate-y-0.5 hover:shadow-[0_24px_70px_color-mix(in_oklch,var(--foreground)_10%,transparent)]">
        <CardHeader className="gap-3 border-b border-border/70 p-5 md:grid-cols-[1fr_auto] md:p-6">
          <div className="flex flex-wrap items-center gap-2">
            <Badge className={impact.className}>
              <ImpactIcon className="size-3" /> {impact.label} · {item.score.toFixed(1)}
            </Badge>
            <Badge variant="outline" className="bg-card">{item.category}</Badge>
            <span className="text-xs text-muted-foreground">{item.market} · {formatDate(item.published_at, true)}</span>
          </div>
          <CardAction className="hidden md:block">
            <span className="grid size-9 place-items-center rounded-full bg-primary/10 text-primary">
              <Target className="size-[18px]" aria-hidden="true" />
            </span>
          </CardAction>
        </CardHeader>
        <CardContent className="grid gap-6 p-5 md:grid-cols-[minmax(0,1fr)_238px] md:p-6">
          <div>
            <p className="eyebrow">今日首要信号 · {item.brand}</p>
            <CardTitle className="mt-2 max-w-3xl font-heading text-[clamp(1.35rem,2.4vw,1.85rem)] font-semibold leading-[1.35] tracking-[-0.035em]">
              {item.title}
            </CardTitle>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-muted-foreground">{item.summary}</p>
            <div className="mt-5 flex flex-wrap items-center gap-2">
              {item.tags.map((tag) => (
                <span key={tag} className="rounded-full bg-muted px-3 py-1.5 text-xs text-muted-foreground"># {tag}</span>
              ))}
              <a
                href={item.source_url}
                target="_blank"
                rel="noreferrer"
                className="ml-auto inline-flex items-center gap-1 text-xs font-medium text-foreground underline-offset-4 hover:text-primary hover:underline"
              >
                {item.source} <ArrowUpRight className="size-3.5" />
              </a>
            </div>
          </div>
          <div className="rounded-2xl bg-foreground p-4 text-background md:p-5">
            <div className="flex items-center gap-2">
              <LensIcon className="size-4 text-primary" />
              <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-background/55">PM Takeaway</p>
            </div>
            <p className="mt-3 text-sm font-medium leading-6">{item.pm_takeaway}</p>
            <div className="mt-5 border-t border-background/15 pt-4">
              <p className="text-[11px] text-background/50">下一步验证</p>
              <p className="mt-1.5 text-xs leading-5 text-background/80">{item.action}</p>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <article className="group relative overflow-hidden rounded-2xl border border-border bg-card p-5 transition-all duration-200 hover:-translate-y-0.5 hover:border-foreground/20 hover:shadow-[0_16px_42px_color-mix(in_oklch,var(--foreground)_7%,transparent)] sm:p-6">
      <span className={`absolute inset-y-0 left-0 w-1 ${item.impact === 'opportunity' ? 'bg-emerald-500' : item.impact === 'risk' ? 'bg-rose-500' : 'bg-amber-500'}`} />
      <div className="flex flex-wrap items-center gap-2">
        <Badge className={impact.className}>
          <ImpactIcon className="size-3" /> {impact.label}
        </Badge>
        <Badge variant="outline">{item.category}</Badge>
        <span className="ml-auto font-mono text-xs text-muted-foreground">{formatDate(item.published_at, true)}</span>
      </div>
      <div className="mt-4 grid gap-5 md:grid-cols-[minmax(0,1fr)_72px]">
        <div>
          <p className="text-xs font-medium text-primary">{item.brand} · {item.market}</p>
          <h3 className="mt-1.5 font-heading text-lg font-semibold leading-[1.45] tracking-[-0.02em] group-hover:text-primary">{item.title}</h3>
          <p className="mt-2 line-clamp-2 text-sm leading-6 text-muted-foreground">{item.summary}</p>
        </div>
        <div className="hidden border-l border-border pl-4 text-right md:block">
          <p className={`font-mono text-2xl font-semibold tracking-[-0.05em] ${scoreTone(item.score)}`}>{item.score.toFixed(1)}</p>
          <p className="mt-1 text-[10px] text-muted-foreground">价值分</p>
          <p className="mt-4 font-mono text-xs text-muted-foreground">{item.confidence}%</p>
          <p className="mt-0.5 text-[10px] text-muted-foreground">可信度</p>
        </div>
      </div>
      <div className="mt-4 rounded-xl bg-muted/70 px-4 py-3">
        <p className="flex items-center gap-1.5 text-[11px] font-semibold text-foreground">
          <Lightbulb className="size-3.5 text-primary" /> 产品经理视角
        </p>
        <p className="mt-1 text-xs leading-5 text-muted-foreground">{item.pm_takeaway}</p>
      </div>
      <div className="mt-4 flex items-center justify-between gap-3 border-t border-border pt-4">
        <div className="flex min-w-0 flex-wrap gap-1.5">
          {item.tags.slice(0, 3).map((tag) => (
            <span key={tag} className="text-[11px] text-muted-foreground">#{tag}</span>
          ))}
        </div>
        <a
          href={item.source_url}
          target="_blank"
          rel="noreferrer"
          aria-label={`查看原文：${item.title}`}
          className="inline-flex shrink-0 items-center gap-1 text-xs font-medium text-foreground hover:text-primary"
        >
          原文 <ArrowUpRight className="size-3.5" />
        </a>
      </div>
    </article>
  );
}

export function RadarApp() {
  const [category, setCategory] = useState('all');
  const [impact, setImpact] = useState<'all' | Impact>('all');
  const [period, setPeriod] = useState('all');
  const [market, setMarket] = useState('all');
  const [query, setQuery] = useState('');
  const searchRef = useRef<HTMLInputElement>(null);

  const markets = useMemo(
    () => Array.from(new Set(data.items.map((item) => item.market))).sort((a, b) => a.localeCompare(b, 'zh-CN')),
    [],
  );

  const categoryCounts = useMemo(() => {
    const counts = new Map<string, number>();
    data.items.forEach((item) => counts.set(item.category, (counts.get(item.category) ?? 0) + 1));
    return counts;
  }, []);

  const filteredItems = useMemo(() => {
    const normalizedQuery = query.trim().toLocaleLowerCase('zh-CN');
    return data.items
      .filter((item) => category === 'all' || item.category === category)
      .filter((item) => impact === 'all' || item.impact === impact)
      .filter((item) => market === 'all' || item.market === market)
      .filter((item) => matchesPeriod(item, period))
      .filter((item) => {
        if (!normalizedQuery) return true;
        return [item.title, item.summary, item.brand, item.market, ...item.tags]
          .join(' ')
          .toLocaleLowerCase('zh-CN')
          .includes(normalizedQuery);
      })
      .sort((a, b) => b.score - a.score || Date.parse(b.published_at) - Date.parse(a.published_at));
  }, [category, impact, market, period, query]);

  const hasFilters = category !== 'all' || impact !== 'all' || market !== 'all' || period !== 'all' || query;
  const opportunityCount = data.items.filter((item) => item.impact === 'opportunity').length;
  const riskCount = data.items.filter((item) => item.impact === 'risk').length;
  const topOpportunities = [...data.items]
    .filter((item) => item.impact === 'opportunity')
    .sort((a, b) => b.score - a.score)
    .slice(0, 3);

  const resetFilters = () => {
    setCategory('all');
    setImpact('all');
    setPeriod('all');
    setMarket('all');
    setQuery('');
  };

  return (
    <main className="min-h-screen bg-background text-foreground">
      <header className="sticky top-0 z-40 border-b border-border/80 bg-background/95 backdrop-blur-xl">
        <div className="mx-auto flex h-16 max-w-[1540px] items-center gap-4 px-4 sm:px-6 xl:px-8">
          <a href="#top" className="flex shrink-0 items-center gap-3" aria-label="渡海首页">
            <span className="grid size-9 place-items-center rounded-xl bg-primary text-primary-foreground shadow-[0_8px_22px_rgba(210,66,35,.2)]">
              <Radar className="size-[18px]" aria-hidden="true" />
            </span>
            <div>
              <p className="font-heading text-[17px] font-semibold leading-none tracking-[-0.02em]">渡海 · 出海情报</p>
              <p className="mt-1 hidden font-mono text-[9px] uppercase tracking-[0.16em] text-muted-foreground sm:block">China brands, global signals</p>
            </div>
          </a>

          <nav className="ml-8 hidden items-center gap-6 text-xs text-muted-foreground lg:flex" aria-label="主导航">
            <a href="#signals" className="font-medium text-foreground">情报流</a>
            <a href="#opportunities" className="transition-colors hover:text-foreground">机会雷达</a>
            <a href="#cadence" className="transition-colors hover:text-foreground">回查机制</a>
          </nav>

          <div className="ml-auto flex items-center gap-2">
            <Button
              variant="outline"
              className="hidden bg-card md:inline-flex"
              onClick={() => searchRef.current?.focus()}
            >
              <Search data-icon="inline-start" /> 搜索情报
            </Button>
            <Button
              className="bg-foreground text-background hover:bg-foreground/85"
              onClick={() => document.querySelector('#signals')?.scrollIntoView({ behavior: 'smooth' })}
            >
              今日简报 <ArrowRight data-icon="inline-end" />
            </Button>
          </div>
        </div>
      </header>

      <div id="top" className="mx-auto grid max-w-[1540px] gap-6 px-4 py-6 sm:px-6 lg:grid-cols-[214px_minmax(0,1fr)] xl:grid-cols-[214px_minmax(0,1fr)_286px] xl:px-8">
        <aside className="hidden lg:block">
          <div className="sticky top-[88px]">
            <p className="eyebrow px-3">情报域</p>
            <nav className="mt-3 space-y-1" aria-label="情报分类">
              {categoryOptions.map((option) => {
                const Icon = option.icon;
                const active = category === option.key;
                const count = option.key === 'all' ? data.items.length : categoryCounts.get(option.key) ?? 0;
                return (
                  <button
                    key={option.key}
                    type="button"
                    onClick={() => setCategory(option.key)}
                    aria-pressed={active}
                    className={`flex w-full items-center gap-2.5 rounded-xl px-3 py-2.5 text-left text-sm transition-all ${
                      active
                        ? 'bg-foreground text-background shadow-sm'
                        : 'text-muted-foreground hover:bg-card hover:text-foreground'
                    }`}
                  >
                    <Icon className="size-4" />
                    <span className="min-w-0 flex-1">{option.label}</span>
                    <span className="font-mono text-[10px] opacity-65">{String(count).padStart(2, '0')}</span>
                  </button>
                );
              })}
            </nav>

            <div id="cadence" className="mt-8 rounded-2xl border border-border bg-card p-4">
              <div className="flex items-center justify-between">
                <p className="eyebrow">巡航节奏</p>
                <RefreshCw className="size-3.5 text-signal" />
              </div>
              <div className="mt-4 space-y-3">
                {[
                  ['每天 11:00', '检查最近 3 天'],
                  ['每周日', '回查本月'],
                  ['每月 1 日', '回查上月'],
                ].map(([title, detail], index) => (
                  <div key={title} className="grid grid-cols-[18px_1fr] gap-2.5">
                    <span className={`mt-1 grid size-[18px] place-items-center rounded-full font-mono text-[8px] ${index === 0 ? 'bg-primary text-primary-foreground' : 'bg-muted text-muted-foreground'}`}>{index + 1}</span>
                    <div>
                      <p className="text-xs font-medium">{title}</p>
                      <p className="mt-0.5 text-[11px] text-muted-foreground">{detail}</p>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </aside>

        <section className="min-w-0">
          <div className="flex flex-col justify-between gap-5 border-b border-border pb-6 md:flex-row md:items-end">
            <div>
              <div className="flex items-center gap-2">
                <span className="size-2 rounded-full bg-signal shadow-[0_0_0_5px_rgba(25,149,119,.10)]" />
                <p className="eyebrow">{formatDateTime(data.meta.generated_at)} 已更新 · {reviewModeCopy[data.meta.review_mode] ?? '自动核查'}</p>
              </div>
              <h1 className="mt-3 max-w-3xl font-heading text-[clamp(1.85rem,4vw,3.35rem)] font-semibold leading-[1.08] tracking-[-0.055em]">把出海噪音，筛成可行动的信号。</h1>
              <p className="mt-3 max-w-2xl text-sm leading-6 text-muted-foreground">为产品经理准备的中国品牌全球化雷达。追踪从货品、包装到获客、下单、履约与回款的完整链路。</p>
            </div>
            <div className="grid min-w-fit grid-cols-3 gap-px overflow-hidden rounded-xl border border-border bg-border text-center">
              {[
                [String(data.items.length).padStart(2, '0'), '本期信号'],
                [String(opportunityCount).padStart(2, '0'), '机会信号'],
                [String(new Set(data.items.map((item) => item.market)).size).padStart(2, '0'), '覆盖市场'],
              ].map(([value, label]) => (
                <div key={label} className="bg-card px-3 py-3 sm:px-4">
                  <p className="font-mono text-xl font-semibold tracking-[-0.04em]">{value}</p>
                  <p className="mt-0.5 whitespace-nowrap text-[10px] text-muted-foreground">{label}</p>
                </div>
              ))}
            </div>
          </div>

          <div className="flex gap-2 overflow-x-auto py-4 [scrollbar-width:none] lg:hidden">
            {categoryOptions.map((option) => (
              <Button
                key={option.key}
                size="sm"
                variant={category === option.key ? 'default' : 'outline'}
                className="shrink-0 bg-card"
                onClick={() => setCategory(option.key)}
              >
                {option.label}
              </Button>
            ))}
          </div>

          <section id="signals" className="scroll-mt-24 pt-5">
            <div className="rounded-2xl border border-border bg-card/75 p-3 shadow-sm backdrop-blur sm:p-4">
              <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
                <div className="relative min-w-0 flex-1">
                  <Search className="pointer-events-none absolute left-3 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
                  <Input
                    ref={searchRef}
                    value={query}
                    onChange={(event) => setQuery(event.target.value)}
                    placeholder="搜索品牌、市场、品类或信号…"
                    aria-label="搜索情报"
                    className="h-10 bg-background pl-9 pr-9"
                  />
                  {query && (
                    <button
                      type="button"
                      onClick={() => setQuery('')}
                      aria-label="清空搜索"
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
                    >
                      <X className="size-4" />
                    </button>
                  )}
                </div>
                <div className="flex flex-wrap items-center gap-2">
                  <NativeSelect value={period} onChange={(event) => setPeriod(event.target.value)} aria-label="选择时间范围" className="flex-1 sm:flex-none">
                    <NativeSelectOption value="all">全部时间</NativeSelectOption>
                    <NativeSelectOption value="3d">最近 3 天</NativeSelectOption>
                    <NativeSelectOption value="month">本月</NativeSelectOption>
                  </NativeSelect>
                  <NativeSelect value={market} onChange={(event) => setMarket(event.target.value)} aria-label="选择市场" className="flex-1 sm:flex-none">
                    <NativeSelectOption value="all">全部市场</NativeSelectOption>
                    {markets.map((itemMarket) => (
                      <NativeSelectOption key={itemMarket} value={itemMarket}>{itemMarket}</NativeSelectOption>
                    ))}
                  </NativeSelect>
                </div>
              </div>
              <div className="mt-3 flex items-center gap-2 overflow-x-auto border-t border-border pt-3 [scrollbar-width:none]">
                <Filter className="mr-1 size-3.5 shrink-0 text-muted-foreground" />
                {[
                  ['all', `全部 ${data.items.length}`],
                  ['opportunity', `机会 ${opportunityCount}`],
                  ['risk', `风险 ${riskCount}`],
                  ['mixed', `混合 ${data.items.length - opportunityCount - riskCount}`],
                ].map(([key, label]) => (
                  <button
                    key={key}
                    type="button"
                    onClick={() => setImpact(key as 'all' | Impact)}
                    aria-pressed={impact === key}
                    className={`shrink-0 rounded-full px-3 py-1.5 text-xs font-medium transition-colors ${impact === key ? 'bg-foreground text-background' : 'bg-muted text-muted-foreground hover:text-foreground'}`}
                  >
                    {label}
                  </button>
                ))}
                <span className="ml-auto shrink-0 text-[11px] text-muted-foreground">按价值分排序</span>
              </div>
            </div>

            <div className="mt-5 flex items-end justify-between gap-4">
              <div>
                <p className="eyebrow">Intelligence Feed</p>
                <h2 className="mt-1 font-heading text-xl font-semibold tracking-tight">值得你关注的变化</h2>
              </div>
              <p className="text-xs text-muted-foreground">找到 {filteredItems.length} 条信号</p>
            </div>

            {filteredItems.length ? (
              <div className="mt-4 space-y-4">
                <SignalCard item={filteredItems[0]} featured />
                {filteredItems.slice(1).map((item) => (
                  <SignalCard key={item.id} item={item} />
                ))}
              </div>
            ) : (
              <div className="mt-4 rounded-2xl border border-dashed border-border bg-card px-6 py-16 text-center">
                <Compass className="mx-auto size-8 text-muted-foreground" />
                <h3 className="mt-3 font-heading text-lg font-semibold">这片海域暂时没有信号</h3>
                <p className="mt-1 text-sm text-muted-foreground">换一个品类、市场或时间范围试试。</p>
                {hasFilters && <Button variant="outline" className="mt-4" onClick={resetFilters}>清除筛选</Button>}
              </div>
            )}
          </section>

          <footer className="mt-10 border-t border-border py-6 text-xs leading-5 text-muted-foreground">
            <p>渡海仅整理公开信息与编辑判断，不构成投资、法律或经营建议。原始事实以链接来源为准。</p>
          </footer>
        </section>

        <aside className="hidden xl:block">
          <div className="sticky top-[88px] space-y-4">
            <section id="opportunities" className="scroll-mt-24 rounded-2xl border border-border bg-card p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Opportunity Radar</p>
                  <h2 className="mt-1 font-heading text-base font-semibold">机会雷达</h2>
                </div>
                <span className="grid size-9 place-items-center rounded-full bg-emerald-50 text-emerald-700 dark:bg-emerald-950 dark:text-emerald-300">
                  <Sparkles className="size-4" />
                </span>
              </div>
              <div className="mt-4 divide-y divide-border">
                {topOpportunities.map((item, index) => (
                  <button
                    key={item.id}
                    type="button"
                    onClick={() => {
                      setQuery(item.brand);
                      document.querySelector('#signals')?.scrollIntoView({ behavior: 'smooth' });
                    }}
                    className="group flex w-full items-start gap-3 py-3 text-left first:pt-0 last:pb-0"
                  >
                    <span className="grid size-6 shrink-0 place-items-center rounded-full bg-muted font-mono text-[10px] text-muted-foreground">0{index + 1}</span>
                    <span className="min-w-0 flex-1">
                      <span className="block text-xs font-medium leading-5 group-hover:text-primary">{item.brand} · {item.market}</span>
                      <span className="mt-0.5 line-clamp-2 block text-[11px] leading-4 text-muted-foreground">{item.title}</span>
                    </span>
                    <span className={`font-mono text-sm font-semibold ${scoreTone(item.score)}`}>{item.score.toFixed(1)}</span>
                  </button>
                ))}
              </div>
            </section>

            <section className="rounded-2xl bg-foreground p-5 text-background">
              <div className="flex items-center justify-between">
                <p className="font-mono text-[10px] uppercase tracking-[0.14em] text-background/55">下次巡航</p>
                <CalendarClock className="size-4 text-primary" />
              </div>
              <p className="mt-3 font-heading text-2xl font-semibold tracking-[-0.04em]">{formatDateTime(data.meta.next_run_at)}</p>
              <p className="mt-1 text-xs text-background/60">上海时间 · 自动运行</p>
              <div className="mt-4 border-t border-background/15 pt-4">
                <p className="text-xs leading-5 text-background/75">下次为月度回查：复核上月全部来源，并补齐迟到或更新的事件。</p>
              </div>
            </section>

            <section className="rounded-2xl border border-border bg-card p-5">
              <div className="flex items-center justify-between">
                <div>
                  <p className="eyebrow">Source Health</p>
                  <h2 className="mt-1 text-sm font-semibold">来源运行状态</h2>
                </div>
                <CheckCircle2 className="size-5 text-signal" />
              </div>
              <div className="mt-4 h-1.5 overflow-hidden rounded-full bg-muted">
                <div
                  className="h-full rounded-full bg-signal"
                  style={{ width: `${Math.round((data.meta.source_health.healthy / Math.max(data.meta.source_health.total, 1)) * 100)}%` }}
                />
              </div>
              <div className="mt-3 flex items-center justify-between text-[11px] text-muted-foreground">
                <span>{data.meta.source_health.healthy} 个正常</span>
                <span>{data.meta.source_health.delayed} 个延迟</span>
              </div>
              <button type="button" onClick={() => setImpact('all')} className="mt-4 flex w-full items-center justify-between rounded-xl bg-muted px-3 py-2.5 text-left text-xs font-medium hover:bg-secondary">
                查看全部来源
                <ChevronRight className="size-3.5 text-muted-foreground" />
              </button>
            </section>
          </div>
        </aside>
      </div>
    </main>
  );
}
