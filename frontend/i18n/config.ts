import { getRequestConfig } from 'next-intl/server';
import { notFound } from 'next/navigation';

export const locales = ['en', 'es', 'fr', 'de', 'zh'] as const;
export type Locale = typeof locales[number];

export const defaultLocale: Locale = 'en';

export const localeNames: Record<Locale, { native: string; english: string; flag: string }> = {
  en: { native: 'English', english: 'English', flag: '🇺🇸' },
  es: { native: 'Español', english: 'Spanish', flag: '🇪🇸' },
  fr: { native: 'Français', english: 'French', flag: '🇫🇷' },
  de: { native: 'Deutsch', english: 'German', flag: '🇩🇪' },
  zh: { native: '中文', english: 'Chinese', flag: '🇨🇳' },
};

export default getRequestConfig(async ({ locale }) => {
  // Validate that the incoming `locale` parameter is valid
  if (!locales.includes(locale as Locale)) {
    notFound();
  }

  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
