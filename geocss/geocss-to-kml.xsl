<!-- -*- indent-tabs-mode: nil -*- -->
<!-- vim:tabstop=2:shiftwidth=2:softtabstop=2:expandtab:
-->
<!--
Transforms GeoRSS feed into Google Earth KML document.

Use any XSL Transformer supporting EXSLT, like xsltproc or Xalan2 (not 1.1)
Usage example:

# xsltproc geocss-to-kml.xsl blah.xml
# java -jar /usr/share/java/xalan2.jar -xsl geocss-to-kml.xsl -in blah.rss

-->

<xsl:stylesheet version='1.0'
  xmlns:xsl="http://www.w3.org/1999/XSL/Transform"
  xmlns:str="http://exslt.org/strings"
  xmlns:georss="http://www.georss.org/georss"
  >
<xsl:output method="xml" omit-xml-declaration="no" indent="yes" />

<xsl:template match="/">

<kml
  xmlns="http://earth.google.com/kml/2.2"
  xmlns:gx="http://www.google.com/kml/ext/2.2"
  xmlns:atom="http://www.w3.org/2005/Atom">

<Document>
  <Folder>
    <name>
      <xsl:value-of select="//channel/title" />
    </name>

    <xsl:for-each select="//channel/item">
      <xsl:variable name="latitude">
        <xsl:value-of select="str:tokenize(normalize-space(./georss:point),' ')[1]" />
      </xsl:variable>
      <xsl:variable name="longitude">
        <xsl:value-of select="str:tokenize(normalize-space(./georss:point),' ')[2]" />
      </xsl:variable>
      <Placemark>
        <name>
          <xsl:value-of select="./title" />
        </name>
        <Point>
          <coordinates>
            <xsl:value-of select="concat($longitude, ',', $latitude)" />
          </coordinates>
        </Point>
      </Placemark>
    </xsl:for-each>

  </Folder>
</Document>
</kml>

</xsl:template>

</xsl:stylesheet>
