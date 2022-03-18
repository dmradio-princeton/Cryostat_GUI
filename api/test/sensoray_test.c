///////////////////////////////////////////////////////////////

//#include <Python.h>
//#include <math.h>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
//#include <termios.h>
//#include <time.h>
//#include <unistd.h>
//#include <sys/stat.h>
//#include <sys/time.h>
#include "app2600.h"		// Linux api to 2600 middleware


// CONSTANTS ////////////////////////////////////////////////////////////////

#define IP_ADDRESS			"10.0.0.10"	// Set this to the MM's IP address.

#define MMHANDLE			0		// This is the first MM in the system, so it is number 0.

#define MSEC_GATEWAY		100			// This many milliseconds before timing out or retry gateway transactions.

#define GATEWAY_RETRIES		50			// Do up to this many gateway retries.

// TYPES ////////////////////////////////////////////////////////////////////////

typedef void	*HX;	// Handle to a gateway transaction object.

// PUBLIC STORAGE ///////////////////////////////////////////////////////////////

u16	nboards;	// Number of detected iom's.
u16 IomType[18];	// Detected iom types.
u8 IomStatus[16];	// Iom status info.

u8 ENCODER_MODE = 0;

IOMPORT	diode2608Port = 5;
IOMPORT hwp2620Port = 8;

// FORWARD REFERENCES ////////////////////////////////////////////////////////////
static u8 cheater(void);

// Pre-existing:
static int	DetectAllIoms( void );
static int	io_exec( HX x );
static HX	CreateTransaction( HBD hbd );

// Lucas thinks these are good ideas?
static u8 	get_S2620_port( void ); // Replace with global constant that gets set when board is initialized!
static u8   get_S2608_port( void );
static int 	init_S26_boards( void );
static int 	get_S26_counts( u32 *counts, u16 *timestamp);
static double	*get_ain_ar( int );
//static double 	*get_counts_ts_ain( u32 *counts, u16 *timestamp);
static int 	close_S26( void );
static int 	reset_IOM( u8 iom_port );


int main(int argc, char** argv)
{
	return (init_S26_boards());
}


////////////////////////////////
// Display gateway error info.

void ShowErrorInfo( u32 gwerr, u8 *IomStatus )
{
	char	errmsg[128];
	int	ExtraInfo = gwerr & ~GWERRMASK;
	u8	status;

	printf("Gateway Error: 0x%X\n", (unsigned int)gwerr);

	switch ( gwerr & GWERRMASK ) {
	case GWERR_IOMSPECIFIC:
		status = IomStatus[ExtraInfo];
		sprintf( errmsg, "Iom-specific error on iomport %d", ExtraInfo );
		printf("Status: 0x%X\n", (unsigned int)status);
		if ( IomStatus ) {
			switch( IomType[ExtraInfo] ) {
			case 2608:
				if ( status & STATUS_2608_CALERR )	
					strcat( errmsg, ": using default cal values" );
				break;
			}
		}
		break;
	case GWERR_BADVALUE:		
		sprintf( errmsg, "Illegal value for argument %d", ExtraInfo );
		break;
	case GWERR_IOMCLOSED:
	  sprintf( errmsg, "Iom is not open" );	
		break;
	case GWERR_IOMERROR:
		sprintf( errmsg, "Iom CERR asserted" );	
		break;
	case GWERR_IOMNORESPOND:
		sprintf( errmsg, "Bad module response from iomport %d", ExtraInfo );
		break;
	case GWERR_IOMRESET:		
		status = IomStatus[ExtraInfo];
		sprintf( errmsg, "Module RST asserted" );	
		if ( IomStatus ) {
			printf( "GWERR_IOMRESET Encountered...\nIomType: %i\n", IomType[ExtraInfo] );	
			switch ( IomType[ExtraInfo] ) {
			case 2620:
				if ( !reset_IOM( get_S2620_port() ) ) 
					// returned 0 (success!)
					printf( "Reset success. Retry gateway exchange\n" );						
				else
					printf( "Shiiit... reset failed. Um. Sorry for the code?\n");	
				break;
			case 2608:
				if ( !reset_IOM( get_S2608_port() ) ) 
					// returned 0 (success!)
					printf( "Reset success. Retrying gateway exchange...\n" );						
				else
					printf( "Shiiit... reset failed. Um. Sorry for the code?\n");	
				break;
			default:
				printf( "Currently don't handle reset on IOM type: %i\n", IomType[ExtraInfo] );
				break;
			}
			
		}	
		break;
	case GWERR_IOMTYPE:
		sprintf( errmsg, "Action not supported by iom type" );	
		break;
	case GWERR_MMCLOSED:
		sprintf( errmsg, "MM is closed" );	
		break;
	case GWERR_MMNORESPOND:		
		sprintf( errmsg, "MM response timed out" );	
		break;
	case GWERR_PACKETSEND:
		sprintf( errmsg, "Failed to send cmd packet" );										
		break;
	case GWERR_TOOLARGE:		
		sprintf( errmsg, "Command or response packet too large" );							
		break;
	case GWERR_XACTALLOC:		
		sprintf( errmsg, "Transaction Object allocation problem" );							
		break;
	default:
		sprintf( errmsg, "Unknown error" );	
		break;
	}
	if (( gwerr & GWERRMASK)!=GWERR_IOMRESET) {
	  printf( "Error (non-fatal): 0x%X (%s).\n", ( int ) gwerr, errmsg );
	}

}


static int reset_IOM( u8 p )
{
	/* Battle the reset...
		Supply with u8 specifying port number of IOM to reset
	*/
	HX x = CreateTransaction( MMHANDLE );
	//printf("Handling reset error...\n");
	S26_Sched2600_ClearStatus( x, p, STATUS_RST);
	//printf("Clearing Status...\n");

	return io_exec( x );
}

/////////////////////////////////////////////////////////////////////////////
// Detect and register all i/o modules connected to the 2601 main module.

int DetectAllIoms( void )
{
	u32     faults;

	// Detect and register all iom's.
	if ( ( faults = S26_RegisterAllIoms( MMHANDLE, MSEC_GATEWAY, &nboards, IomType, IomStatus, GATEWAY_RETRIES ) ) != 0 ) {
		printf("S26_RegisterAllIoms failed?\n");
		printf("Found %d boards though.\n", nboards);
		ShowErrorInfo( faults, IomStatus );
		return 0;       // failed.
	}

	// List the discovered iom's.
	printf( "DETECTED IOM'S:\n" );
	int i;
        for ( i = 0; i < 16; i++ ) 
        	if ( IomType[i] )
        		printf( " port %2.2d: %4.4d\n", i, IomType[i] );

        return 1;       // success.
}


////////////////////////////////////////////////////////
// Start a new transaction.
// Returns non-zero transaction handle if successful.

HX CreateTransaction( HBD hbd )
{
        // Create a new transaction.
        HX x = S26_SchedOpen( hbd, GATEWAY_RETRIES );

        // Report error if transaction couldn't be created.
        if ( x == 0 )
                printf( "Error: S26_SchedOpen() failed to allocate a transaction object.\n" );

        return x;
}

////////////////////////////////
// Execute all scheduled i/o.
// Returns zero if successful.

int io_exec( HX x )
{
        GWERR   err;

        // Execute the scheduled i/o.  Report error if one was detected.
        if ( ( err = S26_SchedExecute( x, MSEC_GATEWAY, IomStatus ) ) != 0 )
                ShowErrorInfo( err, IomStatus );

        return (int)err;
}


//Lucas' Shitty Shit
static int init_S26_boards( void ) 
{
	HX 	x;
	u32 	faults;
	// Open the 2600 api.  Declare one MM in system.
	if ( ( faults = S26_DriverOpen( 1 ) ) != 0 ) {
		printf( "DriverOpen() fault: %d\n", ( int ) faults );
		return 1;
	}

	// Note: We need to supply IP_ADDRESS to S26_BoardOpen!
	// 	Also, second arg is IP address if we want multiple clients!
	if ( ( faults = S26_BoardOpen( MMHANDLE, 0, IP_ADDRESS ) ) != 0 ) {
		printf( "BoardOpen() fault: %d\n", ( int ) faults );
		return 1;
	}
	// Reset the I/O system.
	S26_ResetNetwork( MMHANDLE );
	// Register all iom's.  If no errors, execute!
	if ( DetectAllIoms() ) {
		u8 S2620_port = get_S2620_port();
		if ( S2620_port == -1 ) {
			//printf( "could not find 2620!!!\n" );
			return 1;
		}
		//printf("2620 port: %d\n", ( int ) S2620_port);
		//u8 wdto = 1000;
		x = CreateTransaction( MMHANDLE );
		// Make watchdog timer go to 25 seconds:
		S26_Sched2601_SetWatchdog( x, (unsigned short int) 250);
		// Initialize Encodery things?:
		S26_Sched2620_SetModeEncoder( x, S2620_port, 0, 0, 1, ENCODER_MODE );
		S26_Sched2620_SetModeEncoder( x, S2620_port, 1, 0, 1, ENCODER_MODE );
		S26_Sched2620_SetModeEncoder( x, S2620_port, 2, 0, 1, ENCODER_MODE );
		S26_Sched2620_SetModeEncoder( x, S2620_port, 3, 0, 1, ENCODER_MODE );
		io_exec( x );
	}
	else {
		printf("Error... we're now in that else-clause\n");
		return 1;
	}
	// If you made it this far...
	// Success?
	//printf("According to me, initializing worked\n");
	return 0;
}

static u8 get_S2620_port( void ) {
	return hwp2620Port;
	/*
	int j;
	for (j = 0; j < 16; j++) {
		if (IomType[j] == 2620)
			return j;
	}
	return -1;
	*/
}

static u8 get_S2608_port( void )
{
// I'm not a fan of this guy.
	u8 S2608_port = 0;

	int j;
	for( j = 0; j < 16; j++ )
		if ( IomType[j] == 2608 )
			S2608_port = j;
	
	return S2608_port;
}


static int get_S26_counts( u32 *counts, u16 *timestamp)
{
	u8 S2620_port = get_S2620_port();
	
	HX x = CreateTransaction( MMHANDLE );
	S26_Sched2620_SetControlReg( x, S2620_port, 3, 2);
	S26_Sched2620_GetCounts( x, S2620_port, 3, counts, timestamp);

	if ( io_exec( x ) ) {
	  //printf( "Man... somethin' bad happened.\n" );
		return 1;
	}
	return 0;	
}


static double *get_ain_ar( int iomport_num)
{
	double *ain;
	double ain_tmp[16];

	HX x = CreateTransaction( MMHANDLE );
	S26_Sched2608_GetAins( x, (u8) iomport_num, ain_tmp, 0 );

	// Execute the scheduled i/o and then release the transaction object. 
	if( io_exec( x ) ) {
	  //printf( "Man... somethin' bad happened.\n" );
		return NULL;
	}
	ain = ain_tmp;
	return ain;
}
/*
static double *get_counts_ts_ain( u32 *counts, u16 *timestamp)
{
Fills counts, timestamps, and returns pointer to ain[0]. 
Hence: get_counts_ts_ain!

Kind of a frankenstein, but whatever
	// Man you suck at pointers Lucas:
	double *ain;
	double ain_tmp[16];

	u8 	S2620_port;
	HX 	x;

	S2620_port = get_S2620_port();
	//schedule IOM setup. Prepare data types etc.
	x = CreateTransaction( MMHANDLE );
	// Latch and read counts and timestamp from 2620
	S26_Sched2620_SetControlReg( x, S2620_port, 3, 2 );
	S26_Sched2620_GetCounts( x, S2620_port, 3, counts, timestamp );
	S26_Sched2608_GetAins( x, 6, ain_tmp, 0 );

	// Execute the scheduled i/o and then release the transaction object. 
	if( io_exec( x ) ) {
		printf( "Man... somethin' bad happened.\n" );
	}
	ain = ain_tmp;
	return ain;
}
*/

static int close_S26( void )
{
	S26_DriverClose();	
	return 0;
}
