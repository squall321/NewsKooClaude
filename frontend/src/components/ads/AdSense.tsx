import React, { useEffect } from 'react';

interface AdSenseProps {
  adSlot: string;
  adFormat?: 'auto' | 'fluid' | 'rectangle' | 'vertical' | 'horizontal';
  fullWidthResponsive?: boolean;
  className?: string;
}

/**
 * Google AdSense Component
 *
 * Usage:
 * <AdSense adSlot="1234567890" adFormat="auto" fullWidthResponsive />
 *
 * Note: AdSense script should be loaded in index.html:
 * <script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=ca-pub-XXXXXXXXXXXXXXXX" crossorigin="anonymous"></script>
 */
const AdSense: React.FC<AdSenseProps> = ({
  adSlot,
  adFormat = 'auto',
  fullWidthResponsive = true,
  className = '',
}) => {
  useEffect(() => {
    try {
      // @ts-ignore
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch (err) {
      console.error('AdSense error:', err);
    }
  }, []);

  return (
    <div className={`adsense-container ${className}`}>
      <ins
        className="adsbygoogle"
        style={{ display: 'block' }}
        data-ad-client="ca-pub-XXXXXXXXXXXXXXXX" // TODO: Replace with actual AdSense ID
        data-ad-slot={adSlot}
        data-ad-format={adFormat}
        data-full-width-responsive={fullWidthResponsive ? 'true' : 'false'}
      ></ins>
    </div>
  );
};

export default AdSense;
