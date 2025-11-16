import React from 'react';
import Card from '../common/Card';

interface NativeAdProps {
  position?: number;
}

/**
 * Native Ad Component
 * Blends in with post cards for better UX
 */
const NativeAd: React.FC<NativeAdProps> = ({ position = 0 }) => {
  return (
    <Card className="border-2 border-dashed border-gray-300 bg-gray-50">
      <div className="text-center py-8">
        <p className="text-xs text-gray-500 mb-4">Sponsored</p>
        {/* AdSense In-Feed Ad */}
        <ins
          className="adsbygoogle"
          style={{ display: 'block' }}
          data-ad-format="fluid"
          data-ad-layout-key="-fb+5w+4e-db+86" // TODO: Replace with actual layout key
          data-ad-client="ca-pub-XXXXXXXXXXXXXXXX" // TODO: Replace with actual AdSense ID
          data-ad-slot="YYYYYYYYYY" // TODO: Replace with actual slot ID
        ></ins>
        <script>
          {`(adsbygoogle = window.adsbygoogle || []).push({});`}
        </script>
      </div>
    </Card>
  );
};

export default NativeAd;
