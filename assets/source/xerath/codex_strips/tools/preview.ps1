Add-Type -AssemblyName System.Drawing
$taskOut=Split-Path $PSScriptRoot -Parent
$taskM=Get-Content -LiteralPath (Join-Path $taskOut 'manifest.json') -Raw | ConvertFrom-Json
$taskTags=@('idle','run','attack','skill','skill_quick','skill2','ult','ult_loop','ult_shot','hit','dead')
$taskContact=[System.Drawing.Bitmap]::new(1450,1595)
$taskG=[System.Drawing.Graphics]::FromImage($taskContact)
$taskG.Clear([System.Drawing.Color]::FromArgb(225,232,240))
$taskG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
$taskG.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::Half
$taskFont=[System.Drawing.Font]::new('Arial',12)
foreach($taskTag in $taskTags){
 $taskRow=[Array]::IndexOf($taskTags,$taskTag)
 $taskA=$taskM.animations.$taskTag
 $taskG.DrawString($taskTag,$taskFont,[System.Drawing.Brushes]::Black,4,$taskRow*145+55)
 foreach($taskF in $taskA.frames){
  $taskI=$taskF.frame_index
  $taskFrame=[System.Drawing.Bitmap]::new((Join-Path $taskOut ('preview/'+$taskTag+'_'+('{0:D2}' -f $taskI)+'_1x.png')))
  $taskCropX=$taskF.pivot_1x[0]-40
  $taskRect=[System.Drawing.Rectangle]::new($taskCropX,20,80,66)
  $taskPrev=[System.Drawing.Bitmap]::new(640,528)
  $taskPG=[System.Drawing.Graphics]::FromImage($taskPrev)
  $taskPG.Clear([System.Drawing.Color]::FromArgb(225,232,240))
  $taskPG.InterpolationMode=[System.Drawing.Drawing2D.InterpolationMode]::NearestNeighbor
  $taskPG.PixelOffsetMode=[System.Drawing.Drawing2D.PixelOffsetMode]::Half
  $taskPG.DrawImage($taskFrame,[System.Drawing.Rectangle]::new(0,0,640,528),$taskRect,[System.Drawing.GraphicsUnit]::Pixel)
  $taskPrev.Save((Join-Path $taskOut ('preview/'+$taskTag+'_'+('{0:D2}' -f $taskI)+'_8x.png')))
  $taskG.DrawImage($taskFrame,[System.Drawing.Rectangle]::new(130+$taskI*160,$taskRow*145+13,160,132),$taskRect,[System.Drawing.GraphicsUnit]::Pixel)
  $taskG.DrawString(($taskI+1).ToString()+' / '+$taskF.duration_ms+'ms',$taskFont,[System.Drawing.Brushes]::Black,130+$taskI*160,$taskRow*145)
  $taskPG.Dispose();$taskPrev.Dispose();$taskFrame.Dispose()
 }
}
$taskContact.Save((Join-Path $taskOut 'contact-sheet.png'))
$taskG.Dispose();$taskContact.Dispose();$taskFont.Dispose()


