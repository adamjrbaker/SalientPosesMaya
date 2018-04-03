#define MAX_DIMENSIONS 200

/* Verbosity Level
 *
 * 0 - no output
 * 1 - output from each task
 */
#define VERBOSE 0

/* Measures the high-dimensional point to line distance that corresponds to the
 * distance between a choord spanning two poses and another pose.
 */
float perpendicular_distance(float *start_pose,
                             float *end_pose,
                             float *current_pose,
                             int n_dimensions) {
    int dimension;
    float distance;
    float numerator;
    float denominator;
    float ratio;
    float current_to_start[MAX_DIMENSIONS], end_to_start[MAX_DIMENSIONS];
    float distance_in_one_dimension;

    numerator = 0.0f;
    denominator = 0.0f;
    for (dimension = 0; dimension < n_dimensions; ++dimension) {
        current_to_start[dimension] =  current_pose[dimension] - start_pose[dimension];
        end_to_start[dimension] = end_pose[dimension] - start_pose[dimension];
        
        numerator = numerator + current_to_start[dimension] * end_to_start[dimension];
        denominator = denominator + end_to_start[dimension] * end_to_start[dimension];
    }
    
    distance = 0.0f;
    ratio = numerator / denominator;
    if (denominator != 0.0f) {
        distance = 0.0f;
        for (dimension = 0; dimension < n_dimensions; ++dimension) {
            distance_in_one_dimension = current_to_start[dimension] - ratio * end_to_start[dimension];
            distance = distance + distance_in_one_dimension * distance_in_one_dimension;
        }
        return sqrt(distance);
    } else {
        return 999999999.0f;
    }
}

/* Gets the value corresponding to a given pose and dimension
 */
float get_value_of_dimension_at(__global const float *animation,
                              int pose_index,
                              int dimension,
                              const int n_dimensions)
{
    int animation_index = pose_index * n_dimensions + dimension;
    return animation[animation_index];
}

/* Extracts the values corresponding to a pose by
 * iterating the values of each dimension and storing
 * them in the `pose` collection.
 */
void extract_at(__global const float *animation,
                int pose_index,
                int n_dimensions,
                float *pose)
{
    int dimension;
    int animation_index;
    
    for (dimension = 0; dimension < n_dimensions; ++dimension) {
        float value = get_value_of_dimension_at(animation,
                                                pose_index,
                                                dimension,
                                                n_dimensions);
        pose[dimension] = value;
    }
}

__kernel void max_distance_to_polyline(__global const float *animation,
                                       __global const int   *indices_i,
                                       __global const int   *indices_j,
                                       __global float *output_errors,
                                       __global int *output_indices,
                                       const int n_combinations,
                                       const int n_dimensions)
{
    const int global_id = get_global_id(0);
    const int index_i = indices_i[global_id];
    const int index_j = indices_j[global_id];
    const int frames_for_segment = index_j - index_i + 1;
    
    // Discard threads that aren't used.
    if (global_id > (n_combinations - 1)) {
        return;
    }
    
    int i, j;
    float maximum_distance;
    int maximum_index;
    float current_distance;
    float start_pose[MAX_DIMENSIONS];
    float end_pose[MAX_DIMENSIONS];
    
    // Extract start and end pose
    extract_at(animation, index_i, n_dimensions, start_pose);
    extract_at(animation, index_j, n_dimensions, end_pose);

    int k;
    int current_pose_index;
    float current_pose[MAX_DIMENSIONS];
    
    // Calculate maximum dindices_itance from chord to polyline
    maximum_distance = 0.0f;
    maximum_index = -1;
    for (k = 1; k < frames_for_segment - 1; ++k) {
        
        // Get the current pose
        current_pose_index = index_i + k;
        extract_at(animation, current_pose_index, n_dimensions, current_pose);
        
        // Measure the distance between the choord between the start and end poses and the current pose
        current_distance = perpendicular_distance(start_pose, end_pose, current_pose, n_dimensions);
        if (current_distance > maximum_distance) {
            maximum_distance = current_distance;
            maximum_index = k;
        }
    }

    if (VERBOSE == 1) {
        printf("OpenCL: i=%d j=%d maxdist=%2.6f index=\n", index_i, index_j, maximum_distance, maximum_index);
    }

    // Set output
    output_errors[global_id] = maximum_distance;
    output_indices[global_id] = maximum_index;
}

