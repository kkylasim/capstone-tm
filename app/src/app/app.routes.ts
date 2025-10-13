import { Routes } from '@angular/router';

export const routes: Routes = [
    {
        path: '',
        loadComponent: () => import('./selection-page/selection-page').then(m => m.SelectionPageComponent)
    }
];
