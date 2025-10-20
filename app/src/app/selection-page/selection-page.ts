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
import { MatTooltipModule } from '@angular/material/tooltip';
import { MatDialog } from '@angular/material/dialog';
import { MatDialogModule } from '@angular/material/dialog';
import { PresetDialog } from '../components/preset-dialog/preset-dialog';

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
    MatDialogModule,
    PresetDialog,
    MatDatepickerModule,
    MatNativeDateModule,
    MatListModule,
    MatButtonModule,
    MatTooltipModule
  ],
  templateUrl: './selection-page.html',
  styleUrls: ['./selection-page.scss']
})
export class SelectionPage {
  constructor(private router: Router, private http: HttpClient, private dialog: MatDialog) {
    // const saved = localStorage.getItem('presets');
    // if (saved) this.presets = JSON.parse(saved);
  }

  tenants: string[] = [];
  scenarios = ['Positive', 'Negative', 'Boundary'];
  availableRules: { name: string; description: string }[] = []

  selectedTenant: string | null = null;
  selectedDate: Date | null = null;
  selectedScenario: string | null = null;
  selectedRules: { name: string; description: string }[] = [];
  warningMessage: string = '';

  presets: any[] = [];

  ngOnInit() {
    this.fetchTenants()
  }

  fetchTenants() {
    const apiURL = 'http://localhost:5000/tenants';

    this.http.get<any>(apiURL).subscribe({
      next: (res) => {
        this.tenants = res.tenants;
      },
      error: (err) => {
        console.error('Failed to load tenants:', err)
        this.warningMessage = 'Failed to load tenants from server.';
      }
    })
  }

  onTenantChange() {
    const apiURL = 'http://localhost:5000/tenant-rules';
    const payload = { tenant: this.selectedTenant }
    this.http.post<any>(apiURL, payload).subscribe({
      next: (res) => {
        this.availableRules = res.rules
        this.selectedRules = [];
      },
      error: (err) => {
        console.error('Error loading rules:', err);
        this.warningMessage = 'Failed to load rules for selected tenant.';
      }
    })
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
      transaction_date: this.selectedDate.toISOString().slice(0, 10).replace(/-/g, ''),
      rules: this.selectedRules.map(r => r.name),
      scenario: this.selectedScenario,
    }

    const apiURL = 'http://localhost:5000/generate-data'

    this.http.post<any>(apiURL, payload).subscribe({
      next: (response) => {
        console.log('Response from backend', response);
        this.router.navigate(['/end'], { state: { data: response.results } });
      },
      error: (error) => {
        console.error('Error from backend', error);
        this.warningMessage = '❌ Failed to generate data. Please try again.'
      }
    })
  }

  openPresetDialog() {
    const dialogRef = this.dialog.open(PresetDialog, {
      data: { presets: this.presets },
      width: '600px',
      height: 'auto',
      maxHeight: '60vh',
      autoFocus: false
    });
  
    dialogRef.afterClosed().subscribe((preset: any) => {
      if (preset) {
        // Autofill fields from selected preset
        this.selectedTenant = preset.tenant;
        this.selectedScenario = preset.scenario;
  
        // Fetch the rules for the tenant from the backend
        const apiURL = 'http://localhost:5000/tenant-rules';
        const payload = { tenant: preset.tenant };
        this.http.post<any>(apiURL, payload).subscribe({
          next: (res) => {
            // Set availableRules to all rules for the tenant
            this.availableRules = res.rules;
  
            // Find rule objects for the preset
            const presetRuleObjects = preset.rules
              .map((name: string) => this.availableRules.find(r => r.name === name))
              .filter(Boolean);
  
            // Remove these rules from availableRules
            this.availableRules = this.availableRules.filter(
              r => !preset.rules.includes(r.name)
            );
            // Set as selectedRules
            this.selectedRules = presetRuleObjects;
          },
          error: (err) => {
            console.error('Error loading rules:', err);
            this.warningMessage = 'Failed to load rules for selected tenant.';
          }
        });
      }
    });
  }

  addPreset() {
    if (!this.selectedTenant || !this.selectedScenario || this.selectedRules.length === 0) {
      this.warningMessage = '⚠️ Please select tenant, scenario, and at least one rule before saving a preset.';
      return;
    }
    const presetName = prompt('Enter a name for this preset:');
    if (!presetName) return;

    // Check for duplicate name
    if (this.presets.some(p => p.name.trim().toLowerCase() === presetName.trim().toLowerCase())) {
      this.warningMessage = '⚠️ Preset name already exists. Please choose a different name.';
      return;
    }

    // Check for duplicate fields (tenant, scenario, rules)
    const newRules = this.selectedRules.map(r => r.name).sort();
    if (this.presets.some(p =>
      p.tenant === this.selectedTenant &&
      p.scenario === this.selectedScenario &&
      p.rules.length === newRules.length &&
      [...p.rules].sort().every((rule: string, idx: number) => rule === newRules[idx])
    )) {
      this.warningMessage = '⚠️ A preset with the same tenant, scenario, and rules already exists.';
      return;
    }

    const newPreset = {
      name: presetName,
      tenant: this.selectedTenant,
      scenario: this.selectedScenario,
      rules: this.selectedRules.map(r => r.name)
    };
    this.presets.push(newPreset);
    localStorage.setItem('presets', JSON.stringify(this.presets));

    this.selectedTenant = null;
    this.selectedDate = null;
    this.selectedScenario = null;
    this.selectedRules = [];
    this.availableRules = [];
  }
}
