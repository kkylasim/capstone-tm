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
import { MatIcon, MatIconModule } from '@angular/material/icon';
import { Router } from '@angular/router';

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
  constructor(private router: Router) { }
  tenants = [1, 2, 3];
  scenarios = ['Positive', 'Negative', 'Boundary'];
  selectedTenant: number | null = null;
  selectedDate: Date | null = null;
  selectedScenario: string | null = null;

  availableOptions = ['Option A', 'Option B', 'Option C', 'Option D'];
  selectedOptions: string[] = [];

  warningMessage: string = '';

  moveSelected(selectedItems: any[]) {
    const values = selectedItems.map((x: any) => x.value);
    this.selectedOptions.push(...values);
    this.availableOptions = this.availableOptions.filter(x => !values.includes(x));
  }

  removeSelected(selectedItems: any[]) {
    const values = selectedItems.map((x: any) => x.value);
    this.availableOptions.push(...values);
    this.selectedOptions = this.selectedOptions.filter(
      (x) => !values.includes(x)
    );
  }

  generateData() {
    if (this.selectedTenant == null || this.selectedDate == null || this.selectedOptions.length == 0 || this.selectedScenario == null) {
      this.warningMessage = '⚠️ Please select a tenant, a date, a scenario and at least one option before proceeding.';
      return;
    }

    this.warningMessage = ''
    this.router.navigate(['/end']);
  }
}
