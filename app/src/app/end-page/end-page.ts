import { Component, inject } from '@angular/core';
import { Router, ActivatedRoute } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';
import { HttpClient } from '@angular/common/http';

@Component({
  selector: 'app-end-page',
  standalone: true,
  imports: [CommonModule, MatButtonModule, MatTableModule],
  templateUrl: './end-page.html',
  styleUrl: './end-page.scss'
})
export class EndPage {
  private router = inject(Router)

  displayedColumns: string[] = [];
  dataSource: any[] = [];
  warningMessage: string = ''

  constructor() {
    const isBrowser = typeof window !== 'undefined' && typeof history !== 'undefined';

    let csvData: string | null = null;

    if (isBrowser) {
      csvData = history.state?.data;
    }

    // const csvData = history.state?.data;
    console.log(csvData)

    if (csvData) {
      this.parseCsvAndSetData(csvData)
      sessionStorage.setItem('generatedCsvData', csvData)
    } else {
      const saved = isBrowser ? sessionStorage.getItem('generatedCsvData') : null;
      if (saved) {
        this.parseCsvAndSetData(saved);
      } else {
        this.warningMessage = '⚠️ No data found. Please generate data first.'
        setTimeout(() => this.router.navigate(['']), 1500)
      }
    }
  }

  parseCsvAndSetData(csvText: string) {
    const rows = csvText.trim().split('\n').map(r => r.split(',').map(v => v.trim()));
    if (rows.length === 0) return;

    const headers = rows[0];
    const data = rows.slice(1).map(r => {
      const obj: any = {};
      headers.forEach((h, i) => obj[h] = r[i]);
      return obj;
    });

    this.displayedColumns = headers;
    this.dataSource = data;
  }

  onDownload() {
    const csvData = sessionStorage.getItem('generatedCsvData');
    if (!csvData) return;

    const blob = new Blob([csvData], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_data.csv';
    a.click();
    URL.revokeObjectURL(url);
  }

  onCancel() {
    this.router.navigate(['']);
  }
}
