import { Component, signal } from '@angular/core';
import { RouterOutlet } from '@angular/router';
import { Tenant } from './models/tenant.model';
import { MatFormFieldModule } from '@angular/material/form-field';
import { MatSelectModule } from '@angular/material/select';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet, MatFormFieldModule, MatSelectModule],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  protected readonly title = signal('app');

  tenants: Tenant[] = [
    { name: 'tenant-0', viewValue: 'Tenant 1' },
    { name: 'tenant-1', viewValue: 'Tenant 2' },
    { name: 'tenant-2', viewValue: 'Tenant 3' },
  ];

  scenarios: any[] = [
    { name: 'positive', viewValue: 'Positive' },
    { name: 'negative', viewValue: 'Negative' },
    { name: 'boundary', viewValue: 'Boundary' }
  ]
}
