<!-- -*- indent-tabs-mode: nil -*- -->
<!-- vim:tabstop=2:shiftwidth=2:softtabstop=2:expandtab:
-->
<!--
Transforms GeoRSS feed into comma delimited CSV file.

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
<xsl:output method="text" indent="yes" />

<xsl:template match="/">
    <xsl:for-each select="//channel/item">
      <xsl:variable name="latitude">
        <xsl:value-of select="str:tokenize(normalize-space(./georss:point),' ')[1]" />
      </xsl:variable>
      <xsl:variable name="longitude">
        <xsl:value-of select="str:tokenize(normalize-space(./georss:point),' ')[2]" />
      </xsl:variable>
      <xsl:variable name="placename">
        <xsl:value-of select="./title" />
      </xsl:variable>
      <xsl:value-of select="concat($longitude, ',', $latitude, ',&quot;', $placename, '&quot;')" /><xsl:text>&#10;</xsl:text>
    </xsl:for-each>
</xsl:template>

</xsl:stylesheet>
