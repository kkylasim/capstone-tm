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

    let data: any[] | null = null;

    if (isBrowser) {
      data = history.state?.data;
    }

    if (data && Array.isArray(data) && data.length > 0) {
      this.dataSource = data;
      this.displayedColumns = Object.keys(data[0]);
      sessionStorage.setItem('generatedTableData', JSON.stringify(data));
    } else {
      const saved = isBrowser ? sessionStorage.getItem('generatedTableData') : null;
      if (saved) {
        const parsed = JSON.parse(saved);
        if (parsed && parsed.length > 0) {
          this.dataSource = parsed;
          this.displayedColumns = Object.keys(parsed[0]);
        } else {
          this.warningMessage = '⚠️ No data found. Please generate data first.'
          setTimeout(() => this.router.navigate(['']), 1500)
        }
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
    const data = this.dataSource;

    // Convert each row to your custom format
    const txtRows = data.map(row =>
      `${row.tenant}${row.transaction_date}${row.transaction_id}~##~${row.tenant}~##~CN1021523002118${row.currency}~##~${row.amount}~##~~##~${row.scenario}\n` +
      `${row.rule_id}\n` +
      "0320331~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~TCOECDEGEN~##~~##~~##~CNMNTXN99~##~~##~20320331124925~##~UOB~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~6000~##~CNY~##~~##~~##~~##~~##~~##~~1~##~~##~~##~~##~~##~~##~RBK~##~~##~110~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~CN_CN~##~~##~~##~~##~~##~~##~4832~##~~##~~##~~##~~##~C~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~~##~\n"
    );

    const txtData = txtRows.join('\n');

    const blob = new Blob([txtData], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'generated_data.txt';
    a.click();
    URL.revokeObjectURL(url);
  }

  onCancel() {
    this.router.navigate(['']);
  }
}
