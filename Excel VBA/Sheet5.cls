VERSION 1.0 CLASS
BEGIN
  MultiUse = -1  'True
END
Attribute VB_Name = "Sheet5"
Attribute VB_GlobalNameSpace = False
Attribute VB_Creatable = False
Attribute VB_PredeclaredId = True
Attribute VB_Exposed = True
Option Explicit

Private Sub Worksheet_Change(ByVal Target As Range)

    Dim tbl As ListObject
    Dim itemCol As Range
    Dim unitCol As Range
    Dim changedCell As Range

    Set tbl = Me.ListObjects("Purchases")

    Set itemCol = tbl.ListColumns("Item").DataBodyRange
    Set unitCol = tbl.ListColumns("Unit").DataBodyRange

    ' Only react if change occurs in the Item column
    If Intersect(Target, itemCol) Is Nothing Then Exit Sub

    Application.EnableEvents = False

    For Each changedCell In Intersect(Target, itemCol)
        If Trim(changedCell.Value) <> "" Then
            unitCol.Cells(changedCell.Row - itemCol.Row + 1).Value = _
                GetUnitForItem(changedCell.Value)
        Else
            unitCol.Cells(changedCell.Row - itemCol.Row + 1).ClearContents
        End If
    Next changedCell

    Application.EnableEvents = True

End Sub


