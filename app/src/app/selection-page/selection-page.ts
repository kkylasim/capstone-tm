import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';
import { MatInputModule } from '@angular/material/input';
import { MatDatepickerModule } from '@angular/material/datepicker';
import { MatNativeDateModule } from '@angular/material/core';
import { MatListModule } from '@angular/material/list';
import { MatButtonModule } from '@angular/material/button';
import { MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';
import { HttpClient, provideHttpClient, withFetch } from '@angular/common/http';

@Component({
  selector: 'app-selection-page',
  standalone: true,
  imports: [
    CommonModule,
    FormsModule,
    MatFormFieldModule,
    MatSelectModule,
    MatInputModule,
    MatIconModule,
    MatButtonModule,
    MatDatepickerModule,
    MatNativeDateModule,
    MatListModule,
    MatButtonModule
  ],
  templateUrl: './selection-page.html',
  styleUrls: ['./selection-page.scss']
})
export class SelectionPage {
  constructor(private router: Router, private http: HttpClient) { }
  tenants: string[] = [];
  scenarios = ['Positive', 'Negative', 'Boundary'];
  availableRules: { name: string; description: string }[] = []

  selectedTenant: string | null = null;
  selectedDate: Date | null = null;
  selectedScenario: string | null = null;
  selectedRules: { name: string; description: string }[] = [];
  warningMessage: string = '';

  ngOnInit() {
    this.fetchConfigData()
  }

  fetchConfigData() {
    const apiURL = 'http://localhost:5000/config';

    this.http.get<any>(apiURL).subscribe({
      next: (data) => {
        console.log('Config data received:', data);
        this.tenants = data.tenants || [];
        this.availableRules = data.rules || [];
      },
      error: (err) => {
        console.error('Failed to load config data:', err);
        this.warningMessage = '⚠️ Failed to load configuration data. Please refresh or try again later.';
      }
    });
  }
  moveSelected(selectedItems: any[]) {
    const items = selectedItems.map((x: any) => x.value);
    this.selectedRules.push(...items);
    this.availableRules = this.availableRules.filter(r => !items.includes(r));
  }

  removeSelected(selectedItems: any[]) {
    const items = selectedItems.map((x: any) => x.value);
    this.availableRules.push(...items);
    this.selectedRules = this.selectedRules.filter(r => !items.includes(r))
  }

  generateData() {
    if (this.selectedTenant == null || this.selectedDate == null || this.selectedRules.length == 0 || this.selectedScenario == null) {
      this.warningMessage = '⚠️ Please select a tenant, a date, a scenario and at least one rule before proceeding.';
      return;
    }

    this.warningMessage = ''

    const payload = {
      tenant: this.selectedTenant,
      date: this.selectedDate.toISOString(),
      scenario: this.selectedScenario,
      rules: this.selectedRules,
    }

    const apiURL = 'http://localhost:5000/generate-data'

    this.http.post(apiURL, payload, { responseType: 'text' }).subscribe({
      next: (csvData) => {
        console.log('Response from backend', csvData);
        this.router.navigate(['/end'], { state: { data: csvData } });
      },
      error: (error) => {
        console.error('Error from backend', error);
        this.warningMessage = '❌ Failed to generate data. Please try again.'
      }
    })
  }
}
