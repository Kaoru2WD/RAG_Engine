param([string]$Root)
$ErrorActionPreference = "Stop"

function Add-WordParagraph {
    param($Selection, [string]$Text, [string]$Style = "", [int]$Size = 10, [int]$Bold = 0)
    $Selection.Font.Size = $Size
    $Selection.Font.Bold = $Bold
    $Selection.TypeText($Text)
    $Selection.TypeParagraph()
}

function Save-WordDoc {
    param($Doc, [string]$Path)
    $wdFormatXMLDocument = 12
    $Doc.SaveAs([ref]$Path, [ref]$wdFormatXMLDocument)
}

function New-DocxSamples {
    param([string]$Root)
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false
    $wdCollapseEnd = 0
    $wdSeekMainDocument = 0
    $wdPageBreak = 7

    try {
        $doc1 = $word.Documents.Add()
        $sel = $word.Selection
        Add-WordParagraph -Selection $sel -Text "HILS DC Charging Bench Bring-up Procedure" -Style "Title" -Size 18 -Bold 1
        Add-WordParagraph -Selection $sel -Text "目的: OBC/DC charging 系の HILS ベンチを朝一で立ち上げるための、前提条件・操作順・確認ログをまとめる。" -Size 10
        Add-WordParagraph -Selection $sel -Text "1. Scope" -Style "Heading 1" -Size 13 -Bold 1
        Add-WordParagraph -Selection $sel -Text "対象は Host PC, dSPACE rack, charger ECU, battery simulator, load emulator。通常運転の量産車条件ではなく、観測優先の bench condition を前提とする。" -Size 10
        Add-WordParagraph -Selection $sel -Text "2. Preconditions" -Style "Heading 1" -Size 13 -Bold 1
        $t1 = $doc1.Tables.Add($sel.Range, 4, 3)
        $t1.Cell(1,1).Range.Text = "Item"; $t1.Cell(1,2).Range.Text = "Expected"; $t1.Cell(1,3).Range.Text = "Note"
        $t1.Cell(2,1).Range.Text = "12V PSU"; $t1.Cell(2,2).Range.Text = "13.5 V"; $t1.Cell(2,3).Range.Text = "2 A current limit 以上"
        $t1.Cell(3,1).Range.Text = "HV Simulator"; $t1.Cell(3,2).Range.Text = "365 V standby"; $t1.Cell(3,3).Range.Text = "初期 SOC 55 %"
        $t1.Cell(4,1).Range.Text = "CANoe"; $t1.Cell(4,2).Range.Text = "config loaded"; $t1.Cell(4,3).Range.Text = "log file path fixed"
        $t1.Borders.Enable = 1
        $sel.SetRange($doc1.Content.End - 1, $doc1.Content.End - 1)
        $sel.TypeParagraph()
        Add-WordParagraph -Selection $sel -Text "3. Bench topology" -Style "Heading 1" -Size 13 -Bold 1
        $shape1 = $doc1.Shapes.AddShape(1, 60, 220, 130, 45)
        $shape1.TextFrame.TextRange.Text = "Host PC"
        $shape1.Fill.ForeColor.RGB = 16770229
        $shape2 = $doc1.Shapes.AddShape(1, 220, 220, 130, 45)
        $shape2.TextFrame.TextRange.Text = "dSPACE HIL"
        $shape2.Fill.ForeColor.RGB = 14474460
        $shape3 = $doc1.Shapes.AddShape(1, 390, 220, 130, 45)
        $shape3.TextFrame.TextRange.Text = "Charger ECU"
        $shape3.Fill.ForeColor.RGB = 14277081
        $shape4 = $doc1.Shapes.AddShape(1, 220, 300, 130, 45)
        $shape4.TextFrame.TextRange.Text = "Battery Sim"
        $shape4.Fill.ForeColor.RGB = 16577786
        $line1 = $doc1.Shapes.AddLine(190, 242, 220, 242)
        $line2 = $doc1.Shapes.AddLine(350, 242, 390, 242)
        $line3 = $doc1.Shapes.AddLine(285, 265, 285, 300)
        $doc1.Shapes | ForEach-Object { $_.WrapFormat.Type = 3 }
        $sel.TypeParagraph()
        $sel.TypeParagraph()
        $sel.TypeParagraph()
        $sel.TypeParagraph()
        Add-WordParagraph -Selection $sel -Text "4. Startup steps" -Style "Heading 1" -Size 13 -Bold 1
        $steps1 = @(
            "PSU output on, dSPACE model load, CANoe measurement start.",
            "CHG_ModeReq=Standby を 500 ms 監視し、unexpected wakeup が無いことを確認。",
            "Pilot duty を 5 % -> 10 % -> 50 % に変え、PlugState=Connected を確認。",
            "Precharge complete 後に ChargeEnable=1 を送り、HV current feedback を確認。"
        )
        for ($i = 0; $i -lt $steps1.Count; $i++) {
            Add-WordParagraph -Selection $sel -Text ("{0}. {1}" -f ($i + 1), $steps1[$i]) -Size 10
        }
        Add-WordParagraph -Selection $sel -Text "5. Useful log fragment" -Style "Heading 1" -Size 13 -Bold 1
        Add-WordParagraph -Selection $sel -Text "[07:52:14.201] PilotDuty=10%" -Size 10
        Add-WordParagraph -Selection $sel -Text "[07:52:14.540] PlugState=Connected" -Size 10
        Add-WordParagraph -Selection $sel -Text "[07:52:16.028] ChargeEnable=1, HVCurrent=8.2A" -Size 10
        Save-WordDoc -Doc $doc1 -Path (Join-Path $Root "docx\hils_dc_charging_bringup_procedure.docx")
        $doc1.Close()

        $doc2 = $word.Documents.Add()
        $sel = $word.Selection
        Add-WordParagraph -Selection $sel -Text "CAN Fault Injection Quick Guide" -Style "Title" -Size 18 -Bold 1
        Add-WordParagraph -Selection $sel -Text "目的: fault injection の準備、注入条件、観測ポイント、復帰手順を 2 ページ弱の参照用に圧縮する。" -Size 10
        Add-WordParagraph -Selection $sel -Text "1. Injection families" -Style "Heading 1" -Size 13 -Bold 1
        $t2 = $doc2.Tables.Add($sel.Range, 5, 4)
        $t2.Cell(1,1).Range.Text = "Fault"
        $t2.Cell(1,2).Range.Text = "Trigger"
        $t2.Cell(1,3).Range.Text = "Observe"
        $t2.Cell(1,4).Range.Text = "Reset"
        $t2.Cell(2,1).Range.Text = "alive counter freeze"
        $t2.Cell(2,2).Range.Text = "State=READY"
        $t2.Cell(2,3).Range.Text = "timeout monitor"
        $t2.Cell(2,4).Range.Text = "bus off clear"
        $t2.Cell(3,1).Range.Text = "checksum flip"
        $t2.Cell(3,2).Range.Text = "Torque request > 40Nm"
        $t2.Cell(3,3).Range.Text = "fallback torque"
        $t2.Cell(3,4).Range.Text = "frame restore"
        $t2.Cell(4,1).Range.Text = "message mute"
        $t2.Cell(4,2).Range.Text = "Diag active"
        $t2.Cell(4,3).Range.Text = "session drop"
        $t2.Cell(4,4).Range.Text = "tester present"
        $t2.Cell(5,1).Range.Text = "ID swap"
        $t2.Cell(5,2).Range.Text = "Heartbeat stable"
        $t2.Cell(5,3).Range.Text = "wrong consumer"
        $t2.Cell(5,4).Range.Text = "DBC revert"
        $t2.Borders.Enable = 1
        $sel.SetRange($doc2.Content.End - 1, $doc2.Content.End - 1)
        $sel.TypeParagraph()
        Add-WordParagraph -Selection $sel -Text "2. Decision flow" -Style "Heading 1" -Size 13 -Bold 1
        $f1 = $doc2.Shapes.AddShape(1, 90, 250, 120, 42)
        $f1.TextFrame.TextRange.Text = "Arm template"
        $f2 = $doc2.Shapes.AddShape(1, 250, 250, 150, 42)
        $f2.TextFrame.TextRange.Text = "Inject on trigger"
        $f3 = $doc2.Shapes.AddShape(1, 450, 250, 150, 42)
        $f3.TextFrame.TextRange.Text = "Observe fallback"
        $f4 = $doc2.Shapes.AddShape(1, 250, 335, 150, 42)
        $f4.TextFrame.TextRange.Text = "Reset + clear DTC"
        $doc2.Shapes.AddLine(210, 271, 250, 271) | Out-Null
        $doc2.Shapes.AddLine(400, 271, 450, 271) | Out-Null
        $doc2.Shapes.AddLine(325, 292, 325, 335) | Out-Null
        $doc2.Shapes | ForEach-Object { $_.WrapFormat.Type = 3 }
        $sel.TypeParagraph(); $sel.TypeParagraph(); $sel.TypeParagraph(); $sel.TypeParagraph(); $sel.TypeParagraph()
        Add-WordParagraph -Selection $sel -Text "3. Notes that often matter" -Style "Heading 1" -Size 13 -Bold 1
        Add-WordParagraph -Selection $sel -Text "- trigger condition をログ時刻と同じ粒度で残す。ready後なのか precharge中なのかで意味が変わる。" -Size 10
        Add-WordParagraph -Selection $sel -Text "- reset 手順を fault 毎に固定しない。bus off clear と full ignition cycle は重みが違う。" -Size 10
        Add-WordParagraph -Selection $sel -Text "- inject 成功だけで満足しない。fallback path が期待通り単調に進むかを見る。" -Size 10
        Save-WordDoc -Doc $doc2 -Path (Join-Path $Root "docx\can_fault_injection_quick_guide.docx")
        $doc2.Close()
    }
    finally {
        $word.Quit()
    }
}

function New-PptxSamples {
    param([string]$Root)
    $ppt = New-Object -ComObject PowerPoint.Application
    $ppt.Visible = -1
    try {
        $pres1 = $ppt.Presentations.Add()
        $slide = $pres1.Slides.Add(1, 1)
        $slide.Shapes.Title.TextFrame.TextRange.Text = "HILS Bench Bring-up Review"
        $slide.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "sample deck for chunking / architecture / checklist / issue summary"

        $slide2 = $pres1.Slides.Add(2, 2)
        $slide2.Shapes.Title.TextFrame.TextRange.Text = "Bench Topology"
        $slide2.Shapes.AddShape(1, 60, 120, 160, 60).TextFrame.TextRange.Text = "Host PC"
        $slide2.Shapes.AddShape(1, 280, 120, 160, 60).TextFrame.TextRange.Text = "dSPACE HIL"
        $slide2.Shapes.AddShape(1, 500, 120, 160, 60).TextFrame.TextRange.Text = "VCU ECU"
        $slide2.Shapes.AddShape(1, 280, 260, 160, 60).TextFrame.TextRange.Text = "Battery Sim"
        $slide2.Shapes.AddLine(220, 150, 280, 150) | Out-Null
        $slide2.Shapes.AddLine(440, 150, 500, 150) | Out-Null
        $slide2.Shapes.AddLine(360, 180, 360, 260) | Out-Null
        $tb = $slide2.Shapes.AddTextbox(1, 60, 360, 580, 90)
        $tb.TextFrame.TextRange.Text = "ポイント: ECU, plant, automation の境界が明示される資料は、RAGで 'どこに責務があるか' を拾いやすい。"

        $slide3 = $pres1.Slides.Add(3, 2)
        $slide3.Shapes.Title.TextFrame.TextRange.Text = "Morning Bring-up Checklist"
        $body = $slide3.Shapes.Placeholders.Item(2).TextFrame.TextRange
        $body.Text = "1. PSU / rack / simulator power on`r2. model load and CANoe start`r3. IGN command and precharge monitor`r4. READY confirmation and torque inhibit check`r5. archive logs before next scenario"

        $slide4 = $pres1.Slides.Add(4, 2)
        $slide4.Shapes.Title.TextFrame.TextRange.Text = "Open Issues"
        $tbl = $slide4.Shapes.AddTable(4, 4, 60, 130, 620, 220).Table
        $tbl.Cell(1,1).Shape.TextFrame.TextRange.Text = "ID"
        $tbl.Cell(1,2).Shape.TextFrame.TextRange.Text = "Symptom"
        $tbl.Cell(1,3).Shape.TextFrame.TextRange.Text = "Likely layer"
        $tbl.Cell(1,4).Shape.TextFrame.TextRange.Text = "Status"
        $tbl.Cell(2,1).Shape.TextFrame.TextRange.Text = "B-04"
        $tbl.Cell(2,2).Shape.TextFrame.TextRange.Text = "PRECHARGE stall"
        $tbl.Cell(2,3).Shape.TextFrame.TextRange.Text = "plant init"
        $tbl.Cell(2,4).Shape.TextFrame.TextRange.Text = "open"
        $tbl.Cell(3,1).Shape.TextFrame.TextRange.Text = "B-08"
        $tbl.Cell(3,2).Shape.TextFrame.TextRange.Text = "diag timeout"
        $tbl.Cell(3,3).Shape.TextFrame.TextRange.Text = "gateway"
        $tbl.Cell(3,4).Shape.TextFrame.TextRange.Text = "watch"
        $tbl.Cell(4,1).Shape.TextFrame.TextRange.Text = "B-11"
        $tbl.Cell(4,2).Shape.TextFrame.TextRange.Text = "torque inhibit stuck"
        $tbl.Cell(4,3).Shape.TextFrame.TextRange.Text = "VCU logic"
        $tbl.Cell(4,4).Shape.TextFrame.TextRange.Text = "investigate"
        $pres1.SaveAs((Join-Path $Root "pptx\hils_bench_bringup_review.pptx"))
        $pres1.Close()

        $pres2 = $ppt.Presentations.Add()
        $s1 = $pres2.Slides.Add(1, 1)
        $s1.Shapes.Title.TextFrame.TextRange.Text = "Regenerative Brake HILS Test Report"
        $s1.Shapes.Placeholders.Item(2).TextFrame.TextRange.Text = "sample report deck / mixed evidence types / action-oriented notes"

        $s2 = $pres2.Slides.Add(2, 2)
        $s2.Shapes.Title.TextFrame.TextRange.Text = "Result Summary"
        $t = $s2.Shapes.AddTable(5, 5, 40, 120, 640, 220).Table
        $headers = @("Scenario","Vehicle speed","SOC","Expected","Observed")
        for ($c = 1; $c -le 5; $c++) { $t.Cell(1,$c).Shape.TextFrame.TextRange.Text = $headers[$c-1] }
        $rows = @(
            @("RB-01","40 km/h","55%","regen available","pass"),
            @("RB-02","80 km/h","95%","regen reduced","pass"),
            @("RB-03","20 km/h","30%","blended brake","monitor"),
            @("RB-07","60 km/h","15%","torque cap release","fail")
        )
        for ($r = 0; $r -lt $rows.Count; $r++) {
            for ($c = 0; $c -lt 5; $c++) {
                $t.Cell($r+2,$c+1).Shape.TextFrame.TextRange.Text = $rows[$r][$c]
            }
        }

        $s3 = $pres2.Slides.Add(3, 2)
        $s3.Shapes.Title.TextFrame.TextRange.Text = "Signal Story"
        $s3.Shapes.AddLine(80, 320, 640, 320) | Out-Null
        $s3.Shapes.AddLine(120, 320, 120, 190) | Out-Null
        $s3.Shapes.AddLine(240, 320, 240, 140) | Out-Null
        $s3.Shapes.AddLine(360, 320, 360, 220) | Out-Null
        $s3.Shapes.AddLine(480, 320, 480, 110) | Out-Null
        $s3.Shapes.AddLine(600, 320, 600, 260) | Out-Null
        $note = $s3.Shapes.AddTextbox(1, 60, 360, 620, 90)
        $note.TextFrame.TextRange.Text = "回生トルク立上りと wheel decel が一致しない場合、制御失敗ではなく plant brake drag を疑う。"

        $s4 = $pres2.Slides.Add(4, 2)
        $s4.Shapes.Title.TextFrame.TextRange.Text = "Next Actions"
        $tb2 = $s4.Shapes.Placeholders.Item(2).TextFrame.TextRange
        $tb2.Text = "A. RB-07 の SOC 低条件を再実行`rB. battery internal resistance map を固定して比較`rC. hydraulic brake model drag term を分離計測`rD. report template に trigger / evidence / rollback を追加"
        $pres2.SaveAs((Join-Path $Root "pptx\regenerative_brake_hils_test_report.pptx"))
        $pres2.Close()
    }
    finally {
        $ppt.Quit()
    }
}

function New-ExcelSamples {
    param([string]$Root)
    $excel = New-Object -ComObject Excel.Application
    $excel.Visible = $false
    try {
        $wb1 = $excel.Workbooks.Add()
        $sum = $wb1.Worksheets.Item(1)
        $sum.Name = "Summary"
        $sum.Range("A1").Value2 = "HILS IO Mapping Register"
        $sum.Range("A3").Value2 = "Status"
        $sum.Range("B3").Value2 = "Count"
        $sum.Range("A4").Value2 = "Mapped"
        $sum.Range("A5").Value2 = "Review"
        $sum.Range("A6").Value2 = "Missing"
        $map = $wb1.Worksheets.Add()
        $map.Name = "SignalMap"
        $headers = @("Domain","Signal","Direction","Rate ms","Source","Sink","Status","Comment")
        for ($i = 0; $i -lt $headers.Count; $i++) { $map.Cells.Item(1,$i+1).Value2 = $headers[$i] }
        $data = @(
            @("Power","KL15","In",10,"VCU stub","INV_MAIN","Mapped","boot trigger"),
            @("Power","HVBus","Out",10,"Battery sim","VCU logic","Review","scale check"),
            @("Brake","RegenReq","In",20,"Brake model","VCU logic","Mapped",""),
            @("Diag","TesterPresent","In",100,"CANoe","Gateway","Missing","DBC alias pending"),
            @("Thermal","CoolantTemp","In",20,"Plant","INV_MAIN","Review","sensor filtering"),
            @("Motor","TorqueFeedback","Out",10,"INV_MAIN","Logger","Mapped","")
        )
        for ($r = 0; $r -lt $data.Count; $r++) {
            for ($c = 0; $c -lt $headers.Count; $c++) {
                $map.Cells.Item($r + 2, $c + 1).Value2 = [string]$data[$r][$c]
            }
        }
        $sum.Range("B4").Formula = "=COUNTIF(SignalMap!G:G,""Mapped"")"
        $sum.Range("B5").Formula = "=COUNTIF(SignalMap!G:G,""Review"")"
        $sum.Range("B6").Formula = "=COUNTIF(SignalMap!G:G,""Missing"")"
        $map.Range("A1:H7").Columns.AutoFit() | Out-Null
        $sum.Range("A1:B6").Columns.AutoFit() | Out-Null
        $chart = $sum.Shapes.AddChart2(227, 51, 220, 80, 360, 220).Chart
        $chart.SetSourceData($sum.Range("A3:B6"))
        $chart.ChartTitle.Text = "Mapping status"
        $wb1.SaveAs((Join-Path $Root "excel\hils_io_mapping_register.xlsx"))
        $wb1.Close($true)

        $wb2 = $excel.Workbooks.Add()
        $ws1 = $wb2.Worksheets.Item(1)
        $ws1.Name = "Execution"
        $hs = @("TestID","Feature","Bench","Owner","Priority","Result","Notes")
        for ($i = 0; $i -lt $hs.Count; $i++) { $ws1.Cells.Item(1,$i+1).Value2 = $hs[$i] }
        $rows2 = @(
            @("TC-101","power mode","Bench-A","Kimura","High","Pass","baseline ready"),
            @("TC-107","regen brake","Bench-B","Arai","High","Fail","RB-07 repeat"),
            @("TC-112","diag recovery","Bench-A","Sato","Med","Watch","session linger"),
            @("TC-130","thermal derate","Bench-C","Ito","Med","Pass","level2 reached"),
            @("TC-145","dc charge","Bench-B","Nakamura","Low","Blocked","pilot stub issue")
        )
        for ($r = 0; $r -lt $rows2.Count; $r++) {
            for ($c = 0; $c -lt $hs.Count; $c++) {
                $ws1.Cells.Item($r + 2, $c + 1).Value2 = [string]$rows2[$r][$c]
            }
        }
        $ws2 = $wb2.Worksheets.Add()
        $ws2.Name = "Coverage"
        $ws2.Range("A1").Value2 = "Regression Execution Matrix"
        $ws2.Range("A3").Value2 = "Result"; $ws2.Range("B3").Value2 = "Count"
        $ws2.Range("A4").Value2 = "Pass"
        $ws2.Range("A5").Value2 = "Fail"
        $ws2.Range("A6").Value2 = "Watch"
        $ws2.Range("A7").Value2 = "Blocked"
        $ws2.Range("B4").Formula = "=COUNTIF(Execution!F:F,""Pass"")"
        $ws2.Range("B5").Formula = "=COUNTIF(Execution!F:F,""Fail"")"
        $ws2.Range("B6").Formula = "=COUNTIF(Execution!F:F,""Watch"")"
        $ws2.Range("B7").Formula = "=COUNTIF(Execution!F:F,""Blocked"")"
        $ws1.Range("A1:G6").Columns.AutoFit() | Out-Null
        $ws2.Range("A1:B7").Columns.AutoFit() | Out-Null
        $chart2 = $ws2.Shapes.AddChart2(201, 4, 240, 90, 360, 230).Chart
        $chart2.SetSourceData($ws2.Range("A3:B7"))
        $chart2.ChartTitle.Text = "Execution result count"
        $wb2.SaveAs((Join-Path $Root "excel\regression_execution_matrix.xlsx"))
        $wb2.Close($true)
    }
    finally {
        $excel.Quit()
    }
}

New-DocxSamples -Root $Root
New-PptxSamples -Root $Root
New-ExcelSamples -Root $Root
