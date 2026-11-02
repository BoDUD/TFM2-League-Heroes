Add-Type -AssemblyName System.Drawing
Add-Type -ReferencedAssemblies System.Drawing -TypeDefinition @'
using System;
using System.Drawing;
using System.Drawing.Imaging;
public class HeraldPack {
 public static void Pack(string input,string output,int x,int y,int w,int h,int cw,int ch) {
  string[] colors={"140B1D","24142E","38203F","553157","7D4C7B","272344","383363","4C4987","6263A6","8193C7","9DCADB","684F22","9E7C2E","D4AE46","F5D966","812076","BE20BC","EF39DC","FF83EF"};
  Color[] pal=Array.ConvertAll(colors,s=>ColorTranslator.FromHtml("#"+s));
  using(var src=new Bitmap(input)) using(var dst=new Bitmap(1536,1536,PixelFormat.Format32bppArgb)) {
   int left=((1536-cw*11)/22)*11, top=1386-ch*11;
   using(var g=Graphics.FromImage(dst)) {g.Clear(Color.Transparent);
    for(int cy=0;cy<ch;cy++) for(int cx=0;cx<cw;cx++) {
     int sx=x+(int)((cx+0.5)*w/cw), sy=y+(int)((cy+0.5)*h/ch);
     Color c=src.GetPixel(sx,sy); if(c.A<128) continue;
     Color best=pal[0]; int score=int.MaxValue;
     foreach(Color p in pal) {int dr=c.R-p.R,dg=c.G-p.G,db=c.B-p.B;int d=dr*dr+dg*dg+db*db;if(d<score){score=d;best=p;}}
     using(var b=new SolidBrush(best))g.FillRectangle(b,left+cx*11,top+cy*11,11,11);
    }
   }
   dst.Save(output,ImageFormat.Png);
  }
 }
}
'@
$dest = $PSScriptRoot
[HeraldPack]::Pack("$dest/raw/riftherald-A-generated.png","$dest/riftherald-A.png",198,555,947,688,55,42)
[HeraldPack]::Pack("$dest/raw/riftherald-B-generated.png","$dest/riftherald-B.png",256,481,841,736,50,61)
