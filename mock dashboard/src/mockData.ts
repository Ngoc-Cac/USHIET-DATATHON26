/**
 * Mock Data Generator for Datathon 2026
 * Simulates e-commerce fashion business in Vietnam (2012-2022)
 */

export const YEARS = Array.from({ length: 11 }, (_, i) => 2012 + i);

export const REGIONS = ['North (Hanoi)', 'South (HCM)', 'Central (Da Nang)', 'Mekong Delta', 'Highlands'];
export const CATEGORIES = ['Apparel', 'Accessories', 'Footwear', 'Outerwear'];
export const SEGMENTS = ['Economy', 'Mid-tier', 'Premium', 'Luxury'];
export const CHANNELS = ['Direct Web', 'Facebook Ads', 'TikTok Shop', 'ShopeeMall', 'Lazada', 'Zalo OA'];

export interface YearlyData {
  year: number;
  revenue: number;
  profit: number;
  margin: number;
  orders: number;
  customers: number;
  newCustomers: number;
  repeatCustomers: number;
  returnRate: number;
  rating: number;
  aov: number;
}

export const generateYearlyData = (): YearlyData[] => {
  return YEARS.map((year) => {
    // Growth factors: 2012 starting small, COVID dip in 2020-2021
    const t = year - 2012;
    const growthBase = Math.pow(1.3, t); // 30% YoY growth approx
    const covidFactor = year === 2020 ? 0.85 : year === 2021 ? 1.05 : 1.2;
    
    const revenue = Math.floor(1200000 * growthBase * covidFactor);
    const profit = Math.floor(revenue * (0.15 + (Math.random() * 0.1))); // 15-25% margin
    const margin = (profit / revenue) * 100;
    const orders = Math.floor(revenue / (45 + Math.random() * 20)); // AOV around 55
    const customers = Math.floor(orders * 0.8);
    const newCustomers = Math.floor(customers * (0.6 - (t * 0.02))); // Retention improves over time
    const repeatCustomers = customers - newCustomers;
    const returnRate = 5 + Math.random() * 8; // 5-13%
    const rating = 3.8 + (Math.random() * 1.0);
    const aov = revenue / orders;

    return { year, revenue, profit, margin, orders, customers, newCustomers, repeatCustomers, returnRate, rating, aov };
  });
};

export const REGION_DATA = REGIONS.map(name => ({
  name,
  revenue: 5000000 + Math.random() * 15000000,
  profit: 1000000 + Math.random() * 3000000,
}));

export const CATEGORY_DATA = CATEGORIES.map(name => ({
  name,
  revenue: 8000000 + Math.random() * 12000000,
  margin: 15 + Math.random() * 20,
  profit: 0, // calculated below
})).map(c => ({...c, profit: (c.revenue * c.margin) / 100}));

export const SEGMENT_DATA = SEGMENTS.map(name => ({
  name,
  revenue: 5000000 + Math.random() * 10000000,
  margin: name === 'Luxury' ? 35 : name === 'Premium' ? 25 : 18,
}));

export const CHANNEL_DATA = CHANNELS.map(name => ({
  name,
  revenue: 2000000 + Math.random() * 8000000,
  ordersPerCust: 1.2 + Math.random() * 1.5,
  aov: 40 + Math.random() * 80,
  returnRate: 4 + Math.random() * 10,
}));

export const PRODUCT_SCATTER = Array.from({ length: 40 }, (_, i) => ({
  id: `P-${i}`,
  name: `Product ${i}`,
  revenue: 10000 + Math.random() * 200000,
  margin: 5 + Math.random() * 45,
  units: 100 + Math.floor(Math.random() * 2000),
  category: CATEGORIES[Math.floor(Math.random() * CATEGORIES.length)],
}));

export const OPS_DATA = {
  returnsBySize: [
    { size: 'XS', rate: 14.5 },
    { size: 'S', rate: 12.2 },
    { size: 'M', rate: 8.4 },
    { size: 'L', rate: 9.1 },
    { size: 'XL', rate: 13.8 },
    { size: 'XXL', rate: 16.5 },
  ],
  returnReasons: [
    { reason: 'Size/Fit', count: 450 },
    { reason: 'Color', count: 120 },
    { reason: 'Defective', count: 80 },
    { reason: 'Change Mind', count: 150 },
    { reason: 'Slow Shipping', count: 200 },
  ],
  deliveryVsRating: [
    { days: 1, rating: 4.8 },
    { days: 2, rating: 4.6 },
    { days: 3, rating: 4.4 },
    { days: 4, rating: 4.1 },
    { days: 5, rating: 3.5 },
    { days: 6, rating: 2.8 },
    { days: 7, rating: 2.2 },
  ],
  stockoutVsRevenue: Array.from({ length: 20 }, (_, i) => ({
    stockoutRate: Math.random() * 30,
    lostRevenue: 5000 + Math.random() * 50000,
  }))
};
