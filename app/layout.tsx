import type { Metadata } from 'next';
import { Geist, Geist_Mono } from 'next/font/google';
import './globals.css';

const geistSans = Geist({
  variable: '--font-geist-sans',
  subsets: ['latin'],
});

const geistMono = Geist_Mono({
  variable: '--font-geist-mono',
  subsets: ['latin'],
});

export const metadata: Metadata = {
  metadataBase: new URL('https://duhai-radar.sea.chatgpt.site'),
  title: '渡海｜中国品牌出海情报',
  description: '追踪中国品牌全球化全链路信号：产品、品牌、渠道、履约、支付与合规。',
  openGraph: {
    title: '渡海｜中国品牌出海情报',
    description: '把出海噪音，筛成可行动的信号。',
    type: 'website',
    locale: 'zh_CN',
    images: [
      {
        url: 'og.png',
        width: 1536,
        height: 1024,
        alt: '渡海｜中国品牌出海情报',
      },
    ],
  },
  twitter: {
    card: 'summary_large_image',
    title: '渡海｜中国品牌出海情报',
    description: '把出海噪音，筛成可行动的信号。',
    images: ['og.png'],
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased`}
      >
        {children}
      </body>
    </html>
  );
}
