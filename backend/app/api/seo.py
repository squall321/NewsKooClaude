"""
SEO API
Sitemap 및 SEO 관련 엔드포인트
"""
from flask import Blueprint, Response
from app import db
from app.models.post import Post
from app.models.category import Category
from datetime import datetime

seo_bp = Blueprint('seo', __name__)


@seo_bp.route('/sitemap.xml', methods=['GET'])
def sitemap():
    """
    동적 Sitemap XML 생성

    Returns:
        XML: Sitemap XML 파일
    """
    # Base URL (TODO: Update with actual domain)
    base_url = 'https://newskoo.com'

    # Start XML
    xml = ['<?xml version="1.0" encoding="UTF-8"?>']
    xml.append('<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">')

    # Homepage
    xml.append('  <url>')
    xml.append(f'    <loc>{base_url}/</loc>')
    xml.append(f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>')
    xml.append('    <changefreq>daily</changefreq>')
    xml.append('    <priority>1.0</priority>')
    xml.append('  </url>')

    # Published Posts
    posts = Post.query.filter_by(status='published').order_by(Post.updated_at.desc()).all()
    for post in posts:
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/post/{post.slug}</loc>')
        lastmod = post.updated_at or post.created_at
        xml.append(f'    <lastmod>{lastmod.strftime("%Y-%m-%d")}</lastmod>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.8</priority>')
        xml.append('  </url>')

    # Categories
    categories = Category.query.all()
    for category in categories:
        xml.append('  <url>')
        xml.append(f'    <loc>{base_url}/category/{category.slug}</loc>')
        xml.append(f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>')
        xml.append('    <changefreq>weekly</changefreq>')
        xml.append('    <priority>0.7</priority>')
        xml.append('  </url>')

    # Search page
    xml.append('  <url>')
    xml.append(f'    <loc>{base_url}/search</loc>')
    xml.append(f'    <lastmod>{datetime.utcnow().strftime("%Y-%m-%d")}</lastmod>')
    xml.append('    <changefreq>monthly</changefreq>')
    xml.append('    <priority>0.5</priority>')
    xml.append('  </url>')

    # Close XML
    xml.append('</urlset>')

    # Join and return
    sitemap_xml = '\n'.join(xml)
    return Response(sitemap_xml, mimetype='application/xml')


@seo_bp.route('/robots.txt', methods=['GET'])
def robots():
    """
    Robots.txt 파일 생성

    Returns:
        Text: robots.txt 파일
    """
    lines = [
        'User-agent: *',
        'Allow: /',
        'Disallow: /admin/',
        'Disallow: /api/',
        '',
        'Sitemap: https://newskoo.com/sitemap.xml'
    ]
    return Response('\n'.join(lines), mimetype='text/plain')
