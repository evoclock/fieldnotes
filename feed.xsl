<?xml version="1.0" encoding="UTF-8"?>
<!--
  Renders feed.xml as a readable page when opened in a browser, while leaving it
  a valid RSS feed for readers. Without this, clicking a feed link shows raw XML
  and looks broken to anyone who has not met RSS before.
-->
<xsl:stylesheet version="1.0"
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:atom="http://www.w3.org/2005/Atom">
<xsl:output method="html" encoding="UTF-8" indent="yes"/>

<xsl:template match="/">
<html lang="en">
<head>
<meta charset="utf-8"/>
<meta name="viewport" content="width=device-width, initial-scale=1"/>
<title><xsl:value-of select="rss/channel/title"/> feed</title>
<style>
:root {
  --coal: #151719;
  --panel: #222629;
  --paper: #f0f2f1;
  --muted: #b8c0bd;
  --orange: #e77843;
  --sage: #79c39e;
  --teal: #3fbec1;
}
* { box-sizing: border-box; }
body {
  margin: 0;
  min-height: 100vh;
  background:
    radial-gradient(circle at 15% 0%, rgba(63,190,193,.12), transparent 34rem),
    var(--coal);
  color: var(--muted);
  font: 18px/1.6 system-ui, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
}
main { width: min(760px, calc(100% - 2rem)); margin: 0 auto; padding: 4rem 0 5rem; }
.eyebrow {
  color: var(--sage);
  font-size: .78rem;
  font-weight: 800;
  letter-spacing: .11em;
  text-transform: uppercase;
  margin: 0;
}
h1 { margin: .3rem 0 .6rem; color: var(--paper); font-size: clamp(2rem, 5vw, 3rem); }
.intro { margin: 0 0 2rem; }
.how {
  padding: 1.3rem 1.5rem;
  border: 1px solid rgba(240,242,241,.16);
  border-radius: 14px;
  background: var(--panel);
  margin: 0 0 2.5rem;
}
.how h2 { margin: 0 0 .5rem; color: var(--paper); font-size: 1.1rem; }
.how p { margin: 0 0 .8rem; }
.url {
  display: block;
  padding: .7rem .9rem;
  border-radius: 8px;
  background: var(--coal);
  color: var(--teal);
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: .95rem;
  word-break: break-all;
}
h2.count { color: var(--paper); font-size: 1.1rem; margin: 0 0 1rem; }
article {
  padding: 1.1rem 0;
  border-top: 1px solid rgba(240,242,241,.14);
}
article h3 { margin: 0 0 .3rem; font-size: 1.15rem; line-height: 1.3; }
article h3 a { color: var(--paper); text-decoration: none; }
article h3 a:hover { color: var(--teal); }
.date { color: var(--sage); font-size: .82rem; font-weight: 700; letter-spacing: .06em; text-transform: uppercase; }
article p { margin: .4rem 0 0; }
a { color: var(--sage); }
footer { margin-top: 2.5rem; padding-top: 1.2rem; border-top: 1px solid rgba(240,242,241,.14); font-size: .95rem; }
.back { display: inline-block; margin-bottom: 2rem; color: var(--orange); font-weight: 800; text-decoration: none; }
</style>
</head>
<body>
<main>
  <a class="back" href="{rss/channel/link}">&#8592; <xsl:value-of select="rss/channel/title"/></a>

  <p class="eyebrow">RSS feed</p>
  <h1><xsl:value-of select="rss/channel/title"/></h1>
  <p class="intro"><xsl:value-of select="rss/channel/description"/></p>

  <div class="how">
    <h2>This page is a feed, not an article</h2>
    <p>It updates whenever something new is published. Rather than checking back,
    paste this address into a feed reader and new pieces arrive on their own.</p>
    <code class="url"><xsl:value-of select="rss/channel/atom:link/@href"/></code>
    <p style="margin-top:.9rem">Any reader will do: NetNewsWire, Feedly, Inoreader,
    Reeder, Thunderbird. Most browsers will also hand this page straight to a
    reader if you have one installed.</p>
  </div>

  <h2 class="count">
    <xsl:value-of select="count(rss/channel/item)"/> pieces, most recent first
  </h2>

  <xsl:for-each select="rss/channel/item">
    <article>
      <p class="date"><xsl:value-of select="substring(pubDate, 6, 11)"/></p>
      <h3><a href="{link}"><xsl:value-of select="title"/></a></h3>
      <p><xsl:value-of select="description"/></p>
    </article>
  </xsl:for-each>

  <footer>
    <p>Back to <a href="{rss/channel/link}"><xsl:value-of select="rss/channel/title"/></a>.</p>
  </footer>
</main>
</body>
</html>
</xsl:template>
</xsl:stylesheet>
