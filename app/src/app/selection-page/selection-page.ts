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
export class SelectionPageComponent {
  tenants = [1, 2, 3];
  selectedTenant: number | null = null;
  selectedDate: Date | null = null;

  availableOptions = ['Option A', 'Option B', 'Option C', 'Option D'];
  selectedOptions: string[] = [];

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
    console.log("Generating data...")
  }
}
