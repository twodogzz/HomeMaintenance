VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet2"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

Private Sub Worksheet_Change(ByVal Target As Range)

    ' Check if the changed cells are within Desired_Ranges (low/high range values)
    If Not Intersect(Target, Me.ListObjects("Desired_Ranges").DataBodyRange) Is Nothing Then
        Application.EnableEvents = False
        Call FormatPoolTestResults
        ThisWorkbook.Sheets("Pool Test Log").ListObjects("Pool_Test_log").Range.AutoFilter  ' Refresh sort/filter
        Application.EnableEvents = True
    End If

End Sub


