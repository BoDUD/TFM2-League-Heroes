param([string]$OutputDirectory=(Split-Path $PSScriptRoot -Parent))
$ErrorActionPreference='Stop'
Add-Type -AssemblyName System.Drawing
$taskBase=$OutputDirectory
$taskDesign=[System.Drawing.Bitmap]::new((Join-Path $taskBase 'source/xerath_design_1x.png'))
$taskHead=[System.Drawing.Bitmap]::new((Join-Path $taskBase 'source/xerath_head_1x.png'))
$taskCells=Get-Content -LiteralPath (Join-Path $taskBase 'xerath_cells.json') -Raw | ConvertFrom-Json
$taskEnergy=@('000A6E','003C59','0090F9','016FA8','019CEF','01B3FB','01D8FA','01F8FC','023439','FBFCFC')
$taskParts=@{head=@();body=@();left_arm=@();right_arm=@();left_shoulder=@();right_shoulder=@();torso=@();left_leg=@();right_leg=@()}
$taskPalette=[System.Collections.Generic.HashSet[string]]::new()
for($taskY=0;$taskY -lt 128;$taskY++){for($taskX=0;$taskX -lt 128;$taskX++){
 $taskC=$taskDesign.GetPixel($taskX,$taskY); if($taskC.A -eq 0){continue}
 $taskHex='{0:X2}{1:X2}{2:X2}' -f $taskC.R,$taskC.G,$taskC.B
 [void]$taskPalette.Add($taskHex)
 $taskP=@{x=$taskX;y=$taskY;color=$taskC;hex=$taskHex}
 if($taskHead.GetPixel($taskX,$taskY).A -gt 0){$taskParts.head+=,$taskP;continue}
 if($taskY -ge 75 -and $taskY -le 85 -and $taskX -le 55){$taskParts.left_arm+=,$taskP;continue}
 if($taskY -ge 75 -and $taskY -le 85 -and $taskX -ge 72){$taskParts.right_arm+=,$taskP;continue}
 $taskParts.body+=,$taskP
 if($taskY -ge 86){if($taskX -lt 64){$taskParts.left_leg+=,$taskP}else{$taskParts.right_leg+=,$taskP}}
 elseif($taskY -le 74 -and $taskX -le 59){$taskParts.left_shoulder+=,$taskP}
 elseif($taskY -le 74 -and $taskX -ge 70){$taskParts.right_shoulder+=,$taskP}
 else{$taskParts.torso+=,$taskP}
}}
function Turn-Point([int]$X,[int]$Y,[int]$Angle){
 switch((($Angle%360)+360)%360){0{return ,@($X,$Y)}90{return ,@(-$Y,$X)}180{return ,@(-$X,-$Y)}270{return ,@($Y,-$X)}default{throw 'Only lossless quarter-turn rotations are allowed.'}}
}
function Put-Pixel($Image,[int]$X,[int]$Y,$Color){
 if($X -lt 0 -or $X -ge 128 -or $Y -lt 0 -or $Y -gt 81){throw "Pixel outside safe cell: $X,$Y"}
 $Image.SetPixel($X,$Y,$Color)
}
function Paint-Arm($Image,[string]$Side,[int]$Upper,[int]$Lower,[int]$ShiftX,[int]$ShiftY,[int]$ArmX=0,[int]$ArmY=0){
 $taskAnchorX=if($Side -eq 'left'){53}else{74}
 $taskElbow=Turn-Point 0 5 $Upper
 $taskClaw=@()
 foreach($taskP in $taskParts[($Side+'_arm')]){
  if($taskP.y -lt 80){$taskQ=Turn-Point ($taskP.x-$taskAnchorX) ($taskP.y-75) $Upper;$taskX=$taskAnchorX+$taskQ[0]}
  else{$taskQ=Turn-Point ($taskP.x-$taskAnchorX) ($taskP.y-80) $Lower;$taskX=$taskAnchorX+$taskElbow[0]+$taskQ[0]}
  $taskY=if($taskP.y -lt 80){75+$taskQ[1]}else{75+$taskElbow[1]+$taskQ[1]}
  $taskX+=$ShiftX+$ArmX;$taskY+=$ShiftY+$ArmY
  Put-Pixel $Image $taskX $taskY $taskP.color
  if($taskP.y -ge 80 -and $taskP.hex -in $taskEnergy -and $taskP.hex -ne '000A6E'){$taskClaw+=,@($taskX,$taskY)}
 }
 $taskAvgX=($taskClaw | ForEach-Object {$_[0]} | Measure-Object -Average).Average
 $taskAvgY=($taskClaw | ForEach-Object {$_[1]} | Measure-Object -Average).Average
 return ,@([Math]::Round($taskAvgX,2),[Math]::Round($taskAvgY,2))
}
function Paint-Head($Image,[int]$ShiftX,[int]$ShiftY,[bool]$Dark=$false){
 foreach($taskP in $taskParts.head){
  $taskC=$taskP.color
  if($Dark -and $taskP.hex -in $taskEnergy){$taskC=[System.Drawing.ColorTranslator]::FromHtml('#040208')}
  Put-Pixel $Image ($taskP.x+$ShiftX) ($taskP.y+$ShiftY) $taskC
 }
}
function Paint-Fragment($Image,$Points,[int]$Angle,[int]$Left,[int]$Bottom,[bool]$RemoveEnergy){
 $taskTransformed=@()
 foreach($taskP in $Points){
  if($RemoveEnergy -and $taskP.hex -in $taskEnergy){continue}
  $taskQ=Turn-Point $taskP.x $taskP.y $Angle
  $taskTransformed+=,@{x=$taskQ[0];y=$taskQ[1];color=$taskP.color}
 }
 $taskMinX=($taskTransformed.x | Measure-Object -Minimum).Minimum
 $taskMaxY=($taskTransformed.y | Measure-Object -Maximum).Maximum
 foreach($taskP in $taskTransformed){Put-Pixel $Image ([int]($taskP.x-$taskMinX+$Left)) ([int]($taskP.y-$taskMaxY+$Bottom)) $taskP.color}
}
# Angles [left upper, left lower, right upper, right lower, whole x, whole y].
# Negative 90 means extension toward image right. 180 raises an arm.
$taskPoses=@{
 run=@(@(0,0,0,0,0,0),@(0,0,0,0,0,-1),@(0,0,0,0,0,-1),@(0,0,0,0,0,0),@(0,0,0,0,0,0),@(0,0,0,0,0,-1),@(0,0,0,0,0,-1),@(0,0,0,0,0,0))
 attack=@(@(0,0,180,270,-1,0),@(0,0,180,270,-2,0),@(0,0,-90,0,0,0),@(0,0,-90,-90,1,0),@(0,0,-90,-90,1,0),@(0,0,0,0,0,0))
 skill=@(@(180,90,-90,180,-1,0),@(180,90,180,270,-1,0),@(180,90,180,270,-1,0),@(180,90,180,270,0,0),@(180,90,180,270,-1,0),@(0,0,-90,-90,2,0),@(0,0,0,0,0,0))
 skill_quick=@(@(180,90,-90,180,-1,0),@(180,90,180,270,-1,0),@(180,90,180,270,-1,0),@(0,0,-90,-90,2,0),@(0,0,0,0,0,0))
 skill2=@(@(0,0,180,270,-1,0),@(0,0,180,270,-2,0),@(0,0,-90,-90,2,0),@(0,0,-90,-90,1,0),@(180,90,180,270,0,0),@(0,0,0,0,0,0))
 ult=@(@(0,180,0,180,0,0),@(180,90,180,270,0,-1),@(180,90,180,270,0,-1),@(180,90,180,270,0,-1),@(180,90,-90,-90,0,0))
 ult_loop=@(@(180,90,-90,-90,0,0),@(180,90,-90,-90,0,-1),@(180,90,-90,-90,0,-1),@(180,90,-90,-90,0,0),@(180,90,-90,-90,0,0),@(180,90,-90,-90,0,0))
 ult_shot=@(@(180,90,-90,-90,1,0),@(180,90,-90,-90,1,0),@(180,90,-90,-90,0,0))
 hit=@(@(90,90,-90,-90,-2,0),@(0,0,0,0,0,0))
 dead=@(@(90,90,-90,-90,-1,0),@(90,180,-90,180,-1,-1),@(180,90,180,270,0,-2),@(90,90,-90,-90,0,-1),@(90,90,-90,-90,0,0),@(0,0,0,0,0,0),@(0,0,0,0,0,0),@(0,0,0,0,0,0))
}
$taskCols=@{idle=3;run=4;attack=3;skill=4;skill_quick=3;skill2=3;ult=3;ult_loop=3;ult_shot=3;hit=2;dead=4}
$taskRelease=@{attack=3;skill=5;skill_quick=3;skill2=2;ult_shot=0}
$taskManifest=@{schema_version=1;pixel_scale=8;cell_size_1x=@(128,96);feet_line_row=81;source_design='source/xerath_design_1x.png';route='lossless approved-source part rig, quarter turns and integer translations; no new body drawings';animations=@{}}
$taskSourceManifest=@{parts=@{};poses=$taskPoses}
foreach($taskKey in $taskParts.Keys){$taskSourceManifest.parts[$taskKey]=@{pixels=$taskParts[$taskKey].Count}}
$taskPalette | Sort-Object | ForEach-Object {'#'+$_} | Set-Content -LiteralPath (Join-Path $OutputDirectory 'palette.txt') -Encoding utf8
foreach($taskTag in @('idle','run','attack','skill','skill_quick','skill2','ult','ult_loop','ult_shot','hit','dead')){
 $taskFrames=@($taskCells.tags.$taskTag)
 $taskN=$taskFrames.Count;$taskColumn=$taskCols[$taskTag];$taskRows=[int][Math]::Ceiling($taskN/$taskColumn)
 $taskSheet=[System.Drawing.Bitmap]::new($taskColumn*1024,$taskRows*768)
 $taskSheet1=[System.Drawing.Bitmap]::new($taskColumn*128,$taskRows*96)
 $taskG=[System.Drawing.Graphics]::FromImage($taskSheet)
 $taskFrameRows=@()
 for($taskIndex=0;$taskIndex -lt $taskN;$taskIndex++){
  $taskInfo=$taskFrames[$taskIndex];$taskFrame=[System.Drawing.Bitmap]::new(128,96)
  $taskClaw=$null;$taskDark=$false
  if($taskTag -eq 'idle'){
   # Copy supplied idle pixels exactly; no regeneration or retiming.
   $taskIdle=[System.Drawing.Bitmap]::new((Join-Path $taskBase 'xerath_idle.png'))
   for($taskY=0;$taskY -lt 96;$taskY++){for($taskX=0;$taskX -lt 128;$taskX++){$taskFrame.SetPixel($taskX,$taskY,$taskIdle.GetPixel(($taskIndex%3)*1024+$taskX*8,([int][Math]::Floor($taskIndex/3))*768+$taskY*8))}}
   $taskIdle.Dispose();$taskDX=$taskInfo.pivot[0]-64;$taskDY=-18
  }else{
   $taskPose=$taskPoses[$taskTag][$taskIndex]
   $taskDX=$taskInfo.pivot[0]-64+$taskPose[4];$taskDY=-18+$taskPose[5]
   if($taskTag -eq 'dead' -and $taskIndex -ge 4){
    $taskStage=$taskIndex-4
    if($taskStage -eq 0){
     foreach($taskP in $taskParts.body){$taskMoveX=if($taskP.x -lt 64){-2}else{2};$taskMoveY=if($taskP.y -ge 86){0}else{-1};Put-Pixel $taskFrame ($taskP.x+$taskDX+$taskMoveX) ($taskP.y+$taskDY+$taskMoveY) $taskP.color}
     [void](Paint-Arm $taskFrame 'left' 90 90 $taskDX $taskDY -2 -1)
     [void](Paint-Arm $taskFrame 'right' -90 -90 $taskDX $taskDY 2 -1)
     Paint-Head $taskFrame $taskDX ($taskDY-2)
     $taskDY-=2
    }else{
     $taskPivotX=$taskInfo.pivot[0];$taskFall=if($taskStage -eq 1){-7}else{0}
     Paint-Fragment $taskFrame $taskParts.left_leg 90 ($taskPivotX-15) (81+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.right_leg 270 ($taskPivotX+2) (81+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.left_arm 90 ($taskPivotX-18) (80+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.right_arm 270 ($taskPivotX+8) (80+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.left_shoulder 0 ($taskPivotX-10) (79+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.right_shoulder 90 ($taskPivotX+6) (80+$taskFall) $true
     Paint-Fragment $taskFrame $taskParts.torso 90 ($taskPivotX-6) (81+$taskFall) $true
     $taskDX=$taskPivotX-64;$taskDY=if($taskStage -eq 1){-3}else{7}
     $taskDark=$taskStage -ge 2;Paint-Head $taskFrame $taskDX $taskDY $taskDark
    }
   }else{
    $taskLegShift=if($taskTag -eq 'run'){@(-1,-1,-2,-2,-1,0,0,-1)[$taskIndex]}else{0}
    foreach($taskP in $taskParts.body){
     $taskLX=if($taskTag -eq 'run' -and $taskP.y -ge 86){$taskLegShift}else{0}
     Put-Pixel $taskFrame ($taskP.x+$taskDX+$taskLX) ($taskP.y+$taskDY) $taskP.color
    }
    $taskArmBack=if($taskTag -eq 'run'){-1}else{0}
    [void](Paint-Arm $taskFrame 'left' $taskPose[0] $taskPose[1] $taskDX $taskDY $taskArmBack)
    $taskClaw=Paint-Arm $taskFrame 'right' $taskPose[2] $taskPose[3] $taskDX $taskDY $taskArmBack
    # Preserve the exact approved torso/shoulder/leg pixels in front of the articulated arms.
    foreach($taskP in $taskParts.body){
     $taskLX=if($taskTag -eq 'run' -and $taskP.y -ge 86){$taskLegShift}else{0}
     Put-Pixel $taskFrame ($taskP.x+$taskDX+$taskLX) ($taskP.y+$taskDY) $taskP.color
    }
    Paint-Head $taskFrame $taskDX $taskDY
   }
  }
  $taskMinX=128;$taskMinY=96;$taskMaxX=-1;$taskMaxY=-1;$taskArea=0
  $taskOX=($taskIndex%$taskColumn)*128;$taskOY=([int][Math]::Floor($taskIndex/$taskColumn))*96
  for($taskY=0;$taskY -lt 96;$taskY++){for($taskX=0;$taskX -lt 128;$taskX++){
   $taskC=$taskFrame.GetPixel($taskX,$taskY);$taskSheet1.SetPixel($taskOX+$taskX,$taskOY+$taskY,$taskC)
   if($taskC.A -eq 0){continue}
   $taskArea++;$taskMinX=[Math]::Min($taskMinX,$taskX);$taskMinY=[Math]::Min($taskMinY,$taskY);$taskMaxX=[Math]::Max($taskMaxX,$taskX);$taskMaxY=[Math]::Max($taskMaxY,$taskY)
   $taskBrush=[System.Drawing.SolidBrush]::new($taskC)
   $taskG.FillRectangle($taskBrush,($taskOX+$taskX)*8,($taskOY+$taskY)*8,8,8);$taskBrush.Dispose()
  }}
  $taskFrame.Save((Join-Path $OutputDirectory ('preview/'+$taskTag+'_'+('{0:D2}' -f $taskIndex)+'_1x.png')))
  $taskHeadExact=$true;$taskHeadVisible=0
  foreach($taskP in $taskParts.head){
   $taskExpect=$taskP.color
   if($taskDark -and $taskP.hex -in $taskEnergy){$taskExpect=[System.Drawing.ColorTranslator]::FromHtml('#040208')}
   $taskActual=$taskFrame.GetPixel($taskP.x+$taskDX,$taskP.y+$taskDY)
   if($taskExpect.ToArgb() -ne $taskActual.ToArgb()){$taskHeadExact=$false}
   if($taskActual.A -gt 0){$taskHeadVisible++}
  }
  $taskRow=@{frame_index=$taskIndex;frame_number=$taskIndex+1;duration_ms=$taskInfo.ms;cell_rect_1x=@($taskOX,$taskOY,128,96);cell_rect_8x=@(($taskOX*8),($taskOY*8),1024,768);pivot_1x=@($taskInfo.pivot[0],$taskInfo.pivot[1]);pivot_8x=@(($taskInfo.pivot[0]*8),($taskInfo.pivot[1]*8));bbox_local_1x=@($taskMinX,$taskMinY,($taskMaxX+1),($taskMaxY+1));opaque_pixels=$taskArea;head_translation_from_design=@($taskDX,$taskDY);head_exact=$taskHeadExact;head_visible_pixels=$taskHeadVisible;head_dark_death_exception=$taskDark;release_frame=($taskRelease.ContainsKey($taskTag) -and $taskRelease[$taskTag] -eq $taskIndex);front_claw_centroid_1x=$taskClaw}
  $taskFrameRows+=,$taskRow
  $taskFrame.Dispose()
 }
 if($taskTag -ne 'idle'){$taskSheet.Save((Join-Path $OutputDirectory ('xerath_'+$taskTag+'.png')))}
 $taskSheet1.Save((Join-Path $OutputDirectory ('xerath_'+$taskTag+'_1x.png')))
 $taskManifest.animations[$taskTag]=@{file=('xerath_'+$taskTag+'.png');file_1x=('xerath_'+$taskTag+'_1x.png');size_8x=@(($taskColumn*1024),($taskRows*768));grid=@($taskColumn,$taskRows);frames=$taskFrameRows}
 $taskG.Dispose();$taskSheet.Dispose();$taskSheet1.Dispose()
}
$taskManifest | ConvertTo-Json -Depth 12 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'manifest.json') -Encoding utf8
$taskSourceManifest | ConvertTo-Json -Depth 10 | Set-Content -LiteralPath (Join-Path $OutputDirectory 'rig-plan.json') -Encoding utf8
$taskDesign.Dispose();$taskHead.Dispose()
'Built all 11 sheets including supplied idle.'




