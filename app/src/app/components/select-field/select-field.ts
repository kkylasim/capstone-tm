import {Component, Input} from '@angular/core';
import {FormsModule} from '@angular/forms';
import {MatInputModule} from '@angular/material/input';
import {MatSelectModule} from '@angular/material/select';
import {MatFormFieldModule} from '@angular/material/form-field';

@Component({
  selector: 'app-select-field',
  imports: [FormsModule, MatInputModule, MatSelectModule, MatFormFieldModule ],
  templateUrl: './select-field.html',
  styleUrl: './select-field.scss'
})
export class SelectField {
  @Input() label: string = 'Option';
  @Input() data: any[] = [];
}
