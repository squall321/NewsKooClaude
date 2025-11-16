import React, { useState } from 'react';
// import { motion } from 'framer-motion';
import Button from '../common/Button';

interface SocialShareProps {
  title: string;
  excerpt: string;
  url: string;
}

const SocialShare: React.FC<SocialShareProps> = ({ title, excerpt, url }) => {
  const [copied, setCopied] = useState(false);

  const handleShare = (platform: string) => {
    const fullUrl = window.location.origin + url;
    let shareUrl = '';

    switch (platform) {
      case 'twitter':
        shareUrl = `https://twitter.com/intent/tweet?text=${encodeURIComponent(title)}&url=${encodeURIComponent(fullUrl)}`;
        break;
      case 'facebook':
        shareUrl = `https://www.facebook.com/sharer/sharer.php?u=${encodeURIComponent(fullUrl)}`;
        break;
      case 'linkedin':
        shareUrl = `https://www.linkedin.com/sharing/share-offsite/?url=${encodeURIComponent(fullUrl)}`;
        break;
      case 'kakao':
        // TODO: Implement Kakao Share API
        if (window.Kakao && window.Kakao.Link) {
          window.Kakao.Link.sendDefault({
            objectType: 'feed',
            content: {
              title,
              description: excerpt,
              imageUrl: '',
              link: {
                mobileWebUrl: fullUrl,
                webUrl: fullUrl,
              },
            },
          });
          return;
        }
        break;
      case 'native':
        if (navigator.share) {
          navigator.share({
            title,
            text: excerpt,
            url: fullUrl,
          });
          return;
        }
        break;
      case 'copy':
        navigator.clipboard.writeText(fullUrl);
        setCopied(true);
        setTimeout(() => setCopied(false), 2000);
        return;
    }

    if (shareUrl) {
      window.open(shareUrl, '_blank', 'width=600,height=400');
    }
  };

  return (
    <div className="flex items-center gap-2 flex-wrap">
      <span className="text-sm text-gray-600 mr-2">Share:</span>

      {/* Native Share (Mobile) */}
      {navigator.share && (
        <Button
          size="sm"
          variant="ghost"
          onClick={() => handleShare('native')}
          className="!min-w-0"
          title="Share"
        >
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8.684 13.342C8.886 12.938 9 12.482 9 12c0-.482-.114-.938-.316-1.342m0 2.684a3 3 0 110-2.684m0 2.684l6.632 3.316m-6.632-6l6.632-3.316m0 0a3 3 0 105.367-2.684 3 3 0 00-5.367 2.684zm0 9.316a3 3 0 105.368 2.684 3 3 0 00-5.368-2.684z" />
          </svg>
        </Button>
      )}

      {/* Twitter */}
      <Button
        size="sm"
        variant="ghost"
        onClick={() => handleShare('twitter')}
        className="!min-w-0"
        title="Share on Twitter"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 4.557c-.883.392-1.832.656-2.828.775 1.017-.609 1.798-1.574 2.165-2.724-.951.564-2.005.974-3.127 1.195-.897-.957-2.178-1.555-3.594-1.555-3.179 0-5.515 2.966-4.797 6.045-4.091-.205-7.719-2.165-10.148-5.144-1.29 2.213-.669 5.108 1.523 6.574-.806-.026-1.566-.247-2.229-.616-.054 2.281 1.581 4.415 3.949 4.89-.693.188-1.452.232-2.224.084.626 1.956 2.444 3.379 4.6 3.419-2.07 1.623-4.678 2.348-7.29 2.04 2.179 1.397 4.768 2.212 7.548 2.212 9.142 0 14.307-7.721 13.995-14.646.962-.695 1.797-1.562 2.457-2.549z" />
        </svg>
      </Button>

      {/* Facebook */}
      <Button
        size="sm"
        variant="ghost"
        onClick={() => handleShare('facebook')}
        className="!min-w-0"
        title="Share on Facebook"
      >
        <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 24 24">
          <path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z" />
        </svg>
      </Button>

      {/* Copy Link */}
      <Button
        size="sm"
        variant={copied ? 'primary' : 'ghost'}
        onClick={() => handleShare('copy')}
        className="!min-w-0"
        title={copied ? 'Copied!' : 'Copy link'}
      >
        {copied ? (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
          </svg>
        ) : (
          <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
          </svg>
        )}
      </Button>
    </div>
  );
};

// Extend Window interface for Kakao
declare global {
  interface Window {
    Kakao?: any;
  }
}

export default SocialShare;
