import { Component } from '@angular/core';
import { Router } from '@angular/router';

@Component({
  selector: 'app-end-page',
  imports: [],
  templateUrl: './end-page.html',
  styleUrl: './end-page.scss'
})
export class EndPage {
  constructor(private router: Router) {}

  dataGenerated = "The basic building blocks of an Angular application are NgModules, which provide a compilation context for components. NgModules collect related code into functional sets; an Angular app is defined by a set of NgModules. An app always has at least a root module that enables bootstrapping, and typically has many more feature modules. This allows for better organization and separation of concerns within the application."

  onDownload() {
    console.log("Downloading data...");
  }

  onCancel() {
    this.router.navigate(['']);
  }
}
