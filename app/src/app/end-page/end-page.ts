import { Component } from '@angular/core';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { MatButtonModule } from '@angular/material/button';
import { MatTableModule } from '@angular/material/table';

@Component({
  selector: 'app-end-page',
  imports: [CommonModule, MatButtonModule, MatTableModule],
  templateUrl: './end-page.html',
  styleUrl: './end-page.scss'
})
export class EndPage {
  constructor(private router: Router) {}
  
  displayedColumns: string[] = ['position', 'name', 'weight', 'symbol'];

  dataSource = [
    { position: 1, name: 'Hydrogen', weight: 1.0079, symbol: 'H' },
    { position: 2, name: 'Helium', weight: 4.0026, symbol: 'He' },
    { position: 3, name: 'Lithium', weight: 6.941, symbol: 'Li' },
    { position: 4, name: 'Beryllium', weight: 9.0122, symbol: 'Be' },
  ];

  onDownload() {
    console.log("Downloading data...");
  }

  onCancel() {
    this.router.navigate(['']);
  }
}
