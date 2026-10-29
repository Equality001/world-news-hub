import http.server
import socketserver
import json
import urllib.request
import xml.etree.ElementTree as ET
import urllib.parse

PORT = 8080

# RSS Feed sources (Including Burmese News Sources)
RSS_FEEDS = {
    "bbc_burmese": "https://www.bbc.com/burmese/index.xml",
    "voa_burmese": "https://www.voaburmese.com/api/z-_q_qpeymv",
    "rfa_burmese": "https://www.rfa.org/burmese/rss.xml",
    "bbc": "http://feeds.bbci.co.uk/news/rss.xml",
    "aljazeera": "https://www.aljazeera.com/xml/rss/all.xml",
    "dw": "https://rss.dw.com/xml/rss-en-all",
    "thaipbs": "https://www.thaipbs.or.th/news/rss"
}

class NewsHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/news' or self.path.startswith('/api/news?'):
            self.send_response(200)
            self.send_header('Content-type', 'application/json; charset=utf-8')
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            all_articles = []
            
            for source, url in RSS_FEEDS.items():
                try:
                    req = urllib.request.Request(
                        url, 
                        headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
                    )
                    with urllib.request.urlopen(req, timeout=5) as response:
                        xml_data = response.read()
                        root = ET.fromstring(xml_data)
                        
                        channel = root.find('channel')
                        items = channel.findall('item') if channel is not None else root.findall('.//{http://www.w3.org/2005/Atom}entry')
                        
                        for item in items:
                            if channel is not None:
                                title = item.find('title')
                                link = item.find('link')
                                pubDate = item.find('pubDate')
                                description = item.find('description')
                                
                                title_text = title.text if title is not None and title.text else "No Title"
                                link_text = link.text if link is not None and link.text else "#"
                                date_text = pubDate.text if pubDate is not None and pubDate.text else ""
                                desc_text = description.text if description is not None and description.text else ""
                            else:
                                title = item.find('{http://www.w3.org/2005/Atom}title')
                                link = item.find('{http://www.w3.org/2005/Atom}link')
                                pubDate = item.find('{http://www.w3.org/2005/Atom}updated')
                                
                                title_text = title.text if title is not None and title.text else "No Title"
                                link_text = link.attrib.get('href', '#') if link is not None else "#"
                                date_text = pubDate.text if pubDate is not None and pubDate.text else ""
                                desc_text = ""

                            all_articles.append({
                                "source": source.upper(),
                                "title": title_text,
                                "link": link_text,
                                "published": date_text,
                                "description": desc_text[:200] if desc_text else ""
                            })
                except Exception as e:
                    print(f"Error fetching {source}: {e}")
                    continue
            
            response_data = json.dumps(all_articles, ensure_ascii=False)
            self.wfile.write(response_data.encode('utf-8'))
        else:
            super().do_GET()

with socketserver.TCPServer(("", PORT), NewsHandler) as httpd:
    print(f"Server serving at http://127.0.0.1:{PORT}")
    httpd.serve_forever()
