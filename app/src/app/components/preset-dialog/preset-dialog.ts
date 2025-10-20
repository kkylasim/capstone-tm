import { Component, Inject } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef, MatDialogModule } from '@angular/material/dialog';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatListModule } from '@angular/material/list';
import { MatIconModule } from '@angular/material/icon';
import { MatTooltipModule } from '@angular/material/tooltip';

@Component({
  selector: 'app-preset-dialog',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatDialogModule, MatListModule, MatIconModule, MatTooltipModule],
  templateUrl: './preset-dialog.html',
  styleUrl: './preset-dialog.scss'
})
export class PresetDialog {
  constructor(
    public dialogRef: MatDialogRef<PresetDialog>,
    @Inject(MAT_DIALOG_DATA) public data: any
  ) {
    console.log('Dialog presets:', data.presets);
  }

  selectPreset(index: number) {
    this.dialogRef.close(this.data.presets[index]);
  }

  editPreset(index: number) {
    const preset = this.data.presets[index];
    const newName = prompt('Edit preset name:', preset.name);
    if (newName !== null && newName.trim() !== '') {
      const duplicate = this.data.presets.some((p: any, i: number) =>
        i !== index && p.name.trim().toLowerCase() === newName.trim().toLowerCase()
      );
      if (duplicate) {
        alert('A preset with this name already exists. Please choose a different name.');
        return;
      }
      preset.name = newName.trim();
      // Optionally, you could allow editing other fields here
      localStorage.setItem('presets', JSON.stringify(this.data.presets));
    }
  }

  deletePreset(index: number) {
    if (confirm('Delete this preset?')) {
      this.data.presets.splice(index, 1);
      localStorage.setItem('presets', JSON.stringify(this.data.presets));
    }
  }
}
