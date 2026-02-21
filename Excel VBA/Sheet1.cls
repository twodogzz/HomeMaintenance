VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet1"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit
Private Sub Worksheet_Change(ByVal Target As Range)

'    ' Check if the changed cells are within Pool_Test_log (test results)
'    If Not Intersect(Target, Me.ListObjects("Pool_Test_log").DataBodyRange) Is Nothing Then
'        Application.EnableEvents = False
'        Call FormatPoolTestResults
'        Me.ListObjects("Pool_Test_log").Range.AutoFilter  ' Refresh existing sort/filter
'        Application.EnableEvents = True
'    End If

    Dim lo As ListObject
    Dim rngTable As Range

    On Error GoTo CleanExit

    Set lo = Me.ListObjects("Pool_Test_log") ' <-- MUST match table name exactly

    ' Table may exist but have no data rows
    If lo.DataBodyRange Is Nothing Then Exit Sub
    Set rngTable = lo.DataBodyRange

    ' Check if change intersects table body
    If Intersect(Target, rngTable) Is Nothing Then Exit Sub

    Application.EnableEvents = False

    Call FormatPoolTestResults

    ' Refresh filters/sorts without reapplying
    If lo.AutoFilter.FilterMode Then
        lo.AutoFilter.ApplyFilter
    End If

CleanExit:
    Application.EnableEvents = True
End Sub

