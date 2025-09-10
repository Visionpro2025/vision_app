// ===============================
// FILE: src/lotteries.spec.ts
// ===============================
// Especificaciones formales de 4 loterías para modo conmutado en la app Vision.
// - Quiniela Florida (Día/Noche)
// - Powerball
// - Mega Millions
// - Jersey Cash 5
//
// Notas clave:
// * Todos los horarios se guardan en ET (Eastern Time) y la UI puede convertir a TZ local.
// * La Quiniela Florida se alimenta de fuentes agregadas (no Florida Lottery) — mostrar disclaimer en UI.
// * T100 debe usar los rangos/formatos definidos aquí para validar/expandir jugadas y prevenir errores.

export type LotteryId = 
  | 'quiniela_fl' 
  | 'powerball' 
  | 'megamillions' 
  | 'jersey_cash_5';

export type Weekday = 'Mon'|'Tue'|'Wed'|'Thu'|'Fri'|'Sat'|'Sun';

export interface DrawSlot { 
  label: 'MIDDAY'|'EVENING'|'NIGHT'|'STANDARD'; 
  days: Weekday[]; 
  timeET: string; // HH:MM en ET 
  cutoffET?: string; // HH:MM (si aplica, p.ej. NJ Cash 5) 
}

export interface LotterySpec { 
  id: LotteryId; 
  name: string; 
  logo: string; // ruta asset o URL 
  numberFormat: '2-digits'|'5+1'|'5of45'; 
  ranges: { 
    quiniela?: { 
      min: number; 
      max: number; 
      positions: 3 
    }; 
    pb?: { 
      mainMin: number; 
      mainMax: number; 
      count: number; 
      extraMin: number; 
      extraMax: number 
    }; 
    mm?: { 
      mainMin: number; 
      mainMax: number; 
      count: number; 
      extraMin: number; 
      extraMax: number 
    }; 
    jc5?: { 
      mainMin: number; 
      mainMax: number; 
      count: number 
    }; 
  }; 
  scheduleET: DrawSlot[]; 
  options?: { 
    doublePlay?: boolean; 
    powerPlay?: boolean; 
    megaplier?: boolean; 
    xtra?: boolean; 
    bullseye?: boolean 
  }; 
  sources: { 
    official?: string[]; 
    trusted?: string[]; 
    disclaimer?: string 
  }; 
}

export const LOTTERIES: Record<LotteryId, LotterySpec> = { 
  quiniela_fl: { 
    id: 'quiniela_fl', 
    name: 'Quiniela Florida', 
    logo: '/assets/quiniela-florida.png', 
    numberFormat: '2-digits', 
    ranges: { 
      quiniela: { 
        min: 0, 
        max: 99, 
        positions: 3 
      } 
    }, 
    scheduleET: [ 
      { 
        label: 'MIDDAY', 
        days: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], 
        timeET: '13:30' 
      }, 
      { 
        label: 'NIGHT',  
        days: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], 
        timeET: '21:45' 
      }, 
    ], 
    options: {}, 
    sources: { 
      trusted: [ 
        'https://www.conectate.com.do/loterias/', 
        'https://loteriasdominicanas.com/', 
      ], 
      disclaimer: 'Resultados de fuente agregada; no es juego oficial de Florida Lottery.' 
    } 
  }, 
  powerball: { 
    id: 'powerball', 
    name: 'Powerball', 
    logo: '/assets/powerball.svg', 
    numberFormat: '5+1', 
    ranges: { 
      pb: { 
        mainMin: 1, 
        mainMax: 69, 
        count: 5, 
        extraMin: 1, 
        extraMax: 26 
      } 
    }, 
    scheduleET: [ 
      { 
        label: 'STANDARD', 
        days: ['Mon','Wed','Sat'], 
        timeET: '22:59' 
      }, 
    ], 
    options: { 
      doublePlay: true, 
      powerPlay: true 
    }, 
    sources: { 
      official: [ 
        'https://www.powerball.com/', 
        'https://www.flalottery.com/' 
      ] 
    } 
  }, 
  megamillions: { 
    id: 'megamillions', 
    name: 'Mega Millions', 
    logo: '/assets/megamillions.svg', 
    numberFormat: '5+1', 
    ranges: { 
      mm: { 
        mainMin: 1, 
        mainMax: 70, 
        count: 5, 
        extraMin: 1, 
        extraMax: 25 
      } 
    }, 
    scheduleET: [ 
      { 
        label: 'STANDARD', 
        days: ['Tue','Fri'], 
        timeET: '23:00' 
      }, 
    ], 
    options: { 
      megaplier: true 
    }, 
    sources: { 
      official: ['https://www.megamillions.com/'] 
    } 
  }, 
  jersey_cash_5: { 
    id: 'jersey_cash_5', 
    name: 'Jersey Cash 5', 
    logo: '/assets/njlottery-cash5.svg', 
    numberFormat: '5of45', 
    ranges: { 
      jc5: { 
        mainMin: 1, 
        mainMax: 45, 
        count: 5 
      } 
    }, 
    scheduleET: [ 
      { 
        label: 'STANDARD', 
        days: ['Mon','Tue','Wed','Thu','Fri','Sat','Sun'], 
        timeET: '22:57', 
        cutoffET: '22:53' 
      }, 
    ], 
    options: { 
      xtra: true, 
      bullseye: true 
    }, 
    sources: { 
      official: ['https://www.njlottery.com/en-us/drawgames/jerseycash5.html'] 
    } 
  } 
};

// Helper para obtener placeholders por modo
export function placeholderFor(id: LotteryId): string { 
  switch (id) { 
    case 'quiniela_fl': 
      return 'Ingresa pares 00–99 (ej.: 63, 06, 17)'; 
    case 'powerball': 
      return '5 números únicos 1–69 + Powerball 1–26'; 
    case 'megamillions': 
      return '5 números únicos 1–70 + Mega Ball 1–25'; 
    case 'jersey_cash_5': 
      return '5 números únicos 1–45'; 
  } 
}








