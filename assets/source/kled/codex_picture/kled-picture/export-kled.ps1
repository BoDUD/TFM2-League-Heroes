Add-Type -AssemblyName System.Drawing
$outDir = 'C:/Users/OWNER/Documents/Codex/2026-10-24/new-chat-8/outputs/kled-picture'
function Export-Sprite([string]$name, [double]$scale) {
  $src = [System.Drawing.Bitmap]::new("$outDir/raw/kled-$name-generated.png")
  $left=$src.Width; $top=$src.Height; $right=0; $bottom=0
  for ($y=0; $y -lt $src.Height; $y++) {
    for ($x=0; $x -lt $src.Width; $x++) {
      if ($src.GetPixel($x,$y).A -ge 128) {
        $left=[Math]::Min($left,$x); $top=[Math]::Min($top,$y)
        $right=[Math]::Max($right,$x+1); $bottom=[Math]::Max($bottom,$y+1)
      }
    }
  }
  $height=$bottom-$top; $width=$right-$left
  if ($scale -le 0) { $scale=550.0/$height }
  $w=[int][Math]::Round($width*$scale); $h=[int][Math]::Round($height*$scale)
  $dst=[System.Drawing.Bitmap]::new(1536,1536,[System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
  $dx=[int][Math]::Round((1536-$w)/2.0); $dy=1390-$h
  for ($y=0; $y -lt $h; $y++) {
    for ($x=0; $x -lt $w; $x++) {
      $sx=[Math]::Min($right-1,$left+[int][Math]::Floor(($x+0.5)/$scale))
      $sy=[Math]::Min($bottom-1,$top+[int][Math]::Floor(($y+0.5)/$scale))
      $c=$src.GetPixel($sx,$sy)
      if ($c.A -ge 128) { $dst.SetPixel($dx+$x,$dy+$y,[System.Drawing.Color]::FromArgb(255,$c.R,$c.G,$c.B)) }
    }
  }
  $dst.Save("$outDir/kled-$name.png",[System.Drawing.Imaging.ImageFormat]::Png)
  $src.Dispose(); $dst.Dispose()
  Write-Output "$name bounds=$dx,$dy,$w,$h scale=$scale"
  return $scale
}
$aResult = Export-Sprite 'A' 0
$aResult | Select-Object -First 1
Export-Sprite 'B' ([double]$aResult[-1]) | Select-Object -First 1
